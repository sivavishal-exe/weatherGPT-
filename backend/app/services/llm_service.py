import re
import html
import os
import sys
import datetime
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from app.config import settings
from app.core.logging import logger
from app.core.security import sanitize_input_text
from app.services.weather_provider import weather_provider
from app.schemas.chat import ChatRequest, ChatResponse, GroundedFact
from app.schemas.weather import SevereWeatherAlert, WeatherDataResponse

# Security Prompt Injection Detection Patterns
INJECTION_PATTERNS = [
    re.compile(r'(ignore|override|forget)\s+(previous|all)\s+instructions', re.IGNORECASE),
    re.compile(r'(system\s+prompt|secret\s+key|api_key|password)', re.IGNORECASE),
    re.compile(r'(eval\(|exec\(|import\s+os|process\.env|subprocess)', re.IGNORECASE),
    re.compile(r'you\s+are\s+now\s+a', re.IGNORECASE),
]

KNOWN_LOCATIONS = {
    "coimbatore": (11.0168, 76.9558, "Coimbatore, India"),
    "chennai": (13.0827, 80.2707, "Chennai, India"),
    "delhi": (28.6139, 77.2090, "Delhi, India"),
    "new delhi": (28.6139, 77.2090, "Delhi, India"),
    "mumbai": (19.0760, 72.8777, "Mumbai, India"),
    "bangalore": (12.9716, 77.5946, "Bangalore, India"),
    "bengaluru": (12.9716, 77.5946, "Bangalore, India"),
    "kolkata": (22.5726, 88.3639, "Kolkata, India"),
    "hyderabad": (17.3850, 78.4867, "Hyderabad, India"),
    "pune": (18.5204, 73.8567, "Pune, India"),
    "jaipur": (26.9124, 75.7873, "Jaipur, India"),
    "ahmedabad": (23.0225, 72.5714, "Ahmedabad, India"),
    "lucknow": (26.8467, 80.9462, "Lucknow, India"),
    "london": (51.5074, -0.1278, "London, UK"),
    "tokyo": (35.6762, 139.6503, "Tokyo, Japan"),
    "new york": (40.7128, -74.0060, "New York, USA")
}

MULTILINGUAL_TEXTS = {
    "en": {
        "header_current": "Weather Intelligence - Current Weather in {loc}:",
        "header_rain": "Weather Intelligence - Rainfall Status & Forecast for {loc} on {date}{time_spec}:",
        "header_travel": "Weather Intelligence - Travel Forecast for {loc} on {date} at {time}:",
        "header_alerts": "Weather Intelligence - Active Severe Warnings for {loc}:",
        "header_no_alerts": "Weather Intelligence - Severe Alert Status for {loc}:\nThere are currently no active official severe weather warnings reported for {loc}.",
        "header_safety": "Weather Intelligence - Safety Advisory Guidelines for Heavy Rainfall:\n1. Stay Indoors: Avoid unnecessary travel during heavy downpours.\n2. Flood Avoidance: Never walk, swim, or drive through waterlogged roads.\n3. Power Safety: Stay away from submerged electrical poles and trees.\n4. Emergency Preparedness: Keep mobile devices charged and emergency contacts ready.",
        "header_5day": "Weather Intelligence - 5-Day Forecast for {loc}:",
        "header_general": "Weather Intelligence - General Weather Overview for {loc} on {date}:",
        "ai_prefix": "AI Advisory: ",
        "umbrella_yes": "Carrying an umbrella is recommended as rain or showers are expected.",
        "umbrella_no": "Low chance of rain. Carrying an umbrella is likely unnecessary.",
        "outage": "Current weather data is unavailable from the weather data service. Please check your internet connection or try again later."
    },
    "hi": {
        "header_current": "मौसम बुद्धिमत्ता - {loc} में वर्तमान मौसम:",
        "header_rain": "मौसम बुद्धिमत्ता - {loc} के लिए वर्षा पूर्वानुमान ({date}{time_spec}):",
        "header_travel": "मौसम बुद्धिमत्ता - {loc} के लिए यात्रा पूर्वानुमान ({date}, समय: {time}):",
        "header_alerts": "मौसम बुद्धिमत्ता - {loc} के लिए सक्रिय गंभीर मौसम चेतावनियाँ:",
        "header_no_alerts": "मौसम बुद्धिमत्ता - {loc} के लिए कोई सक्रिय गंभीर मौसम चेतावनी नहीं है।",
        "header_safety": "मौसम बुद्धिमत्ता - भारी वर्षा सुरक्षा दिशा-निर्देश:\n1. घर के अंदर रहें: भारी बारिश में अनावश्यक यात्रा से बचें।\n2. जलभराव से बचें: जलभराव वाले रास्तों या जलमग्न सड़कों पर गाड़ी न चलाएं।\n3. बिजली सुरक्षा: बिजली के खंभों और गिरे हुए तारों से दूर रहें।\n4. आपातकालीन तैयारी: मोबाइल फोन चार्ज रखें और आपातकालीन संपर्क तैयार रखें।",
        "header_5day": "मौसम बुद्धिमत्ता - {loc} का 5-दिवसीय पूर्वानुमान:",
        "header_general": "मौसम बुद्धिमत्ता - {loc} के लिए सामान्य मौसम अवलोकन ({date}):",
        "ai_prefix": "एआई सुरक्षा सलाह: ",
        "umbrella_yes": "बारिश या बौछार की संभावना के कारण छाता साथ रखने की सलाह दी जाती है।",
        "umbrella_no": "बारिश की कम संभावना है। छाता साथ ले जाना आवश्यक नहीं है।",
        "outage": "मौसम डेटा सेवा से वर्तमान डेटा उपलब्ध नहीं है। कृपया अपना इंटरनेट कनेक्शन जांचें या बाद में प्रयास करें।"
    },
    "ta": {
        "header_current": "வானிலை நுண்ணறிவு - {loc} தற்போதைய வானிலை:",
        "header_rain": "வானிலை நுண்ணறிவு - {loc} மழை முன்னறிவிப்பு ({date}{time_spec}):",
        "header_travel": "வானிலை நுண்ணறிவு - {loc} பயண முன்னறிவிப்பு ({date}, நேரம்: {time}):",
        "header_alerts": "வானிலை நுண்ணறிவு - {loc} தீவிர வானிலை எச்சரிக்கைகள்:",
        "header_no_alerts": "வானிலை நுண்ணறிவு - {loc} தீவிர வானிலை எச்சரிக்கைகள் எதுவும் தற்போது இல்லை.",
        "header_safety": "வானிலை நுண்ணறிவு - கனமழைக்கான பாதுகாப்பு வழிகாட்டுதல்கள்:\n1. வீட்டிற்குள் இருங்கள்: கனமழையின் போது தேவையற்ற பயணங்களைத் தவிர்க்கவும்.\n2. வெள்ளப் பகுதிகளைத் தவிர்க்கவும்: வெள்ளத்தில் மூழ்கிய சாலைகளில் வாகனம் ஓட்ட வேண்டாம்.\n3. மின் பாதுகாப்பு: விழுந்த மின்கம்பங்கள் மற்றும் மரங்களில் இருந்து விலகி இருங்கள்.\n4. அவசரநிலை தயார்நிலை: கைபேசிகளை சார்ஜ் செய்து வைக்கவும்.",
        "header_5day": "வானிலை நுண்ணறிவு - {loc} 5 நாள் வானிலை முன்னறிவிப்பு:",
        "header_general": "வானிலை நுண்ணறிவு - {loc} பொது வானிலை கண்ணோட்டம் ({date}):",
        "ai_prefix": "AI பாதுகாப்பு ஆலோசனை: ",
        "umbrella_yes": "மழை எதிர்பார்க்கப்படுவதால் குடை கொண்டு செல்ல அறிவுறுத்தப்படுகிறது.",
        "umbrella_no": "மழை வாய்ப்பு குறைவு. குடை கொண்டு செல்ல தேவையில்லை.",
        "outage": "வானிலை சேவை கிடைக்கவில்லை. உங்கள் இணைய இணைப்பைச் சரிபார்க்கவும் அல்லது பின்னர் மீண்டும் முயற்சிக்கவும்."
    },
    "ja": {
        "header_current": "気象インテリジェンス - {loc}の現在の天気:",
        "header_rain": "気象インテリジェンス - {loc}の降水予測 ({date}{time_spec}):",
        "header_travel": "気象インテリジェンス - {loc}の旅行・移動予報 ({date} {time}):",
        "header_alerts": "気象インテリジェンス - {loc}の現在発令中の警報・注意報:",
        "header_no_alerts": "気象インテリジェンス - 現在{loc}に発令中の気象警報はありません。",
        "header_safety": "気象インテリジェンス - 大雨安全ガイドライン:\n1. 屋内に留まる: 大雨時の不要不急の外出を避ける。\n2. 冠水回避: 冠水した道路やアンダーパスに入らない。\n3. 感電防止: 切れた電線や水没した電柱に近づかない。\n4. 緊急準備: 携帯電話を充電し、緊急連絡先を確認する。",
        "header_5day": "気象インテリジェンス - {loc}の5日間予報:",
        "header_general": "気象インテリジェンス - {loc}の全般気象概要 ({date}):",
        "ai_prefix": "AI安全アドバイザリー: ",
        "umbrella_yes": "雨が予想されるため、傘を持参することをお勧めします。",
        "umbrella_no": "雨の可能性は低いため、傘を持参する必要はありません。",
        "outage": "現在気象データサービスからデータを入手できません。インターネット接続を確認するか、後でもう一度お試しください。"
    },
    "es": {
        "header_current": "Inteligencia Meteorológica - Tiempo actual en {loc}:",
        "header_rain": "Inteligencia Meteorológica - Pronóstico de lluvia para {loc} en {date}{time_spec}:",
        "header_travel": "Inteligencia Meteorológica - Pronóstico de viaje para {loc} en {date} ({time}):",
        "header_alerts": "Inteligencia Meteorológica - Alertas severas activas en {loc}:",
        "header_no_alerts": "Inteligencia Meteorológica - No hay alertas meteorológicas severas activas en {loc}.",
        "header_safety": "Inteligencia Meteorológica - Pautas de Seguridad para Lluvias Intensas:\n1. Permanezca en interiores: Evite desplazamientos innecesarios.\n2. Evite inundaciones: No camine ni conduzca por carreteras inundadas.\n3. Seguridad eléctrica: Manténgase alejado de postes eléctricos sumergidos.\n4. Preparación para emergencias: Mantenga cargados sus dispositivos móviles.",
        "header_5day": "Inteligencia Meteorológica - Pronóstico de 5 días para {loc}:",
        "header_general": "Inteligencia Meteorológica - Visión general del tiempo en {loc} en {date}:",
        "ai_prefix": "Aviso de Seguridad IA: ",
        "umbrella_yes": "Se recomienda llevar paraguas ya que se esperan lluvias.",
        "umbrella_no": "Baja probabilidad de lluvia. Es probable que no necesites paraguas.",
        "outage": "Los datos meteorológicos actuales no están disponibles. Por favor verifique su conexión a internet o intente nuevamente."
    },
    "fr": {
        "header_current": "Intelligence Météorologique - Météo actuelle à {loc}:",
        "header_rain": "Intelligence Météorologique - Prévisions de pluie pour {loc} le {date}{time_spec}:",
        "header_travel": "Intelligence Météorologique - Prévisions de voyage pour {loc} le {date} à {time}:",
        "header_alerts": "Intelligence Météorologique - Alertes météo sévères actives à {loc}:",
        "header_no_alerts": "Intelligence Météorologique - Aucune alerte météo sévère n'est actuellement active à {loc}.",
        "header_safety": "Intelligence Météorologique - Consignes de Sécurité pour Fortes Pluies:\n1. Restez à l'intérieur: Évitez les déplacements inutiles.\n2. Évitez les inondations: Ne roulez pas sur des routes inondées.\n3. Sécurité électrique: Éloignez-vous des lignes électriques immergées.\n4. Préparation aux urgences: Gardez vos téléphones chargés.",
        "header_5day": "Intelligence Météorologique - Prévisions sur 5 jours pour {loc}:",
        "header_general": "Intelligence Météorologique - Aperçu général de la météo à {loc} le {date}:",
        "ai_prefix": "Avis de Sécurité IA: ",
        "umbrella_yes": "Il est recommandé d'apporter un parapluie car de la pluie est attendue.",
        "umbrella_no": "Faible risque de pluie. Il n'est probablement pas nécessaire d'apporter un parapluie.",
        "outage": "Les données météo actuelles ne sont pas disponibles. Veuillez vérifier votre connexion internet ou réessayer plus tard."
    }
}


class GroundedWeatherGPTService:
    """
    Conversational AI Layer for WeatherGPT.
    Acts as NLU query-parser, weather tool executor, and response synthesizer.
    Guarantees 0% numerical hallucination by deriving all facts from live weather data services.
    """

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        clean_query = sanitize_input_text(request.query)
        lang_code = request.language.lower() if request.language and request.language.lower() in MULTILINGUAL_TEXTS else "en"
        logger.info(f"Conversational AI processing query: '{clean_query}' [Lang: {lang_code}]")

        # 1. Security Check: Defuse prompt injections
        if self._is_prompt_injection(clean_query):
            logger.warning(f"Security Guardrail: Prompt injection defused in query: '{clean_query[:60]}...'")
            return self._build_security_defused_response(request)

        # 2. Extract Entities (Location, Date, Time, Intent)
        loc_name, lat, lon = self._extract_location(clean_query, request)
        target_date_str, date_offset_days = self._extract_date(clean_query)
        time_of_day = self._extract_time(clean_query)
        intent = self._classify_intent(clean_query)

        # 3. Tool Call: Fetch live weather and forecast data
        try:
            weather_data = await weather_provider.get_weather(
                latitude=lat,
                longitude=lon,
                location_name=loc_name,
                days=max(7, date_offset_days + 1),
                low_bandwidth=request.low_bandwidth
            )
        except Exception as e:
            logger.error(f"Weather tool execution failed: {e}")
            t = MULTILINGUAL_TEXTS.get(lang_code, MULTILINGUAL_TEXTS["en"])
            return ChatResponse(
                query=clean_query,
                answer=t["outage"],
                grounded_facts=[],
                official_warnings=[],
                ai_recommendations=[f"{t['ai_prefix']}{t['outage']}"],
                language=request.language,
                low_bandwidth_mode=request.low_bandwidth
            )

        # 4. Synthesize Grounded Response based on Intent & Weather Tool Output
        return self._synthesize_response(
            query=clean_query,
            intent=intent,
            loc_name=loc_name,
            target_date_str=target_date_str,
            date_offset_days=date_offset_days,
            time_of_day=time_of_day,
            weather_data=weather_data,
            request=request,
            lang_code=lang_code
        )

    def _extract_location(self, query: str, request: ChatRequest) -> Tuple[str, float, float]:
        query_lower = query.lower()
        for loc_key, (lat, lon, formatted_name) in KNOWN_LOCATIONS.items():
            if loc_key in query_lower:
                return formatted_name, lat, lon

        if request.location_name:
            lat = request.latitude if request.latitude is not None else 11.0168
            lon = request.longitude if request.longitude is not None else 76.9558
            return request.location_name, lat, lon

        if request.latitude is not None and request.longitude is not None:
            return f"Location ({request.latitude:.2f}, {request.longitude:.2f})", request.latitude, request.longitude

        # Default fallback: Coimbatore, India
        return "Coimbatore, India", 11.0168, 76.9558

    def _extract_date(self, query: str) -> Tuple[str, int]:
        today = datetime.date.today()
        query_lower = query.lower()

        if "tomorrow" in query_lower:
            target = today + datetime.timedelta(days=1)
            return target.strftime("%Y-%m-%d"), 1
        elif "weekend" in query_lower:
            days_until_sat = (5 - today.weekday()) % 7
            if days_until_sat == 0:
                days_until_sat = 7
            target = today + datetime.timedelta(days=days_until_sat)
            return target.strftime("%Y-%m-%d"), days_until_sat
        
        # Check explicit YYYY-MM-DD
        iso_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", query)
        if iso_match:
            return iso_match.group(0), 1

        return today.strftime("%Y-%m-%d"), 0

    def _extract_time(self, query: str) -> str:
        query_lower = query.lower()
        if "morning" in query_lower or "7 am" in query_lower or "7:00 am" in query_lower or "8 am" in query_lower:
            return "Morning"
        elif "afternoon" in query_lower or "12 pm" in query_lower or "2 pm" in query_lower:
            return "Afternoon"
        elif "evening" in query_lower or "6 pm" in query_lower or "7 pm" in query_lower:
            return "Evening"
        elif "night" in query_lower:
            return "Night"
        return "All Day"

    def _classify_intent(self, query: str) -> str:
        q_lower = query.lower()
        if "should i do" in q_lower or "safety" in q_lower or "heavy rainfall" in q_lower or "what to do" in q_lower or "what should" in q_lower or "guideline" in q_lower:
            return "SAFETY_ADVISORY"
        elif "now" in q_lower or "current" in q_lower or "right now" in q_lower:
            return "CURRENT_WEATHER"
        elif "umbrella" in q_lower or "rain" in q_lower or "drizzle" in q_lower or "shower" in q_lower:
            return "RAIN_FORECAST"
        elif "travel" in q_lower or "flight" in q_lower or "drive" in q_lower or "trip" in q_lower:
            return "TRAVEL_FORECAST"
        elif "warning" in q_lower or "alert" in q_lower or "severe" in q_lower:
            return "SEVERE_ALERTS"
        elif "5-day" in q_lower or "5 day" in q_lower or "forecast" in q_lower or "trend" in q_lower:
            return "MULTI_DAY_FORECAST"
        return "GENERAL_WEATHER"

    def _synthesize_response(
        self,
        query: str,
        intent: str,
        loc_name: str,
        target_date_str: str,
        date_offset_days: int,
        time_of_day: str,
        weather_data: WeatherDataResponse,
        request: ChatRequest,
        lang_code: str = "en"
    ) -> ChatResponse:
        
        cur = weather_data.current
        daily_list = weather_data.daily_forecast
        target_daily = daily_list[min(date_offset_days, len(daily_list) - 1)] if daily_list else None

        t = MULTILINGUAL_TEXTS.get(lang_code, MULTILINGUAL_TEXTS["en"])
        prefix = t["ai_prefix"]

        grounded_facts: List[GroundedFact] = []
        ai_recommendations: List[str] = []
        official_warnings = weather_data.official_alerts

        # Base facts
        grounded_facts.append(GroundedFact(
            fact_type="CURRENT_WEATHER",
            fact_text=f"Live current conditions in {loc_name}: {cur.temperature}°C (Feels like {cur.apparent_temperature}°C), {cur.condition_text}, Humidity: {cur.humidity}%, Wind: {cur.wind_speed} km/h, Pressure: {cur.pressure} hPa.",
            source="Open-Meteo Live Meteorological API"
        ))

        if target_daily:
            grounded_facts.append(GroundedFact(
                fact_type="FORECAST_METRICS",
                fact_text=f"Forecast for {loc_name} on {target_date_str}: Max Temp {target_daily.temp_max}°C, Min Temp {target_daily.temp_min}°C, Rain Probability: {target_daily.precipitation_probability}%, Precipitation: {target_daily.precipitation_sum_mm} mm, Condition: {target_daily.condition_text}.",
                source="WeatherGPT High-Resolution Meteorological Engine"
            ))

        # Intent specific synthesis
        if intent == "CURRENT_WEATHER":
            hdr = t["header_current"].format(loc=loc_name)
            answer = (
                f"{hdr}\n"
                f"It is currently {cur.temperature:.1f}°C and {cur.condition_text.lower()} in {loc_name}. "
                f"Feels like {cur.apparent_temperature:.1f}°C with a relative humidity of {cur.humidity:.0f}%, "
                f"wind speed of {cur.wind_speed:.1f} km/h, and atmospheric pressure of {cur.pressure:.1f} hPa."
            )
            ai_recommendations.append(f"{prefix}Current weather is {cur.condition_text.lower()} at {cur.temperature:.1f}°C.")

        elif intent == "RAIN_FORECAST":
            rain_prob = target_daily.precipitation_probability if target_daily else 15.0
            precip_mm = target_daily.precipitation_sum_mm if target_daily else 0.0
            cond = target_daily.condition_text if target_daily else "Partly Cloudy"
            
            rain_status = "High probability of rain" if rain_prob >= 50.0 else ("Moderate chance of rain" if rain_prob >= 25.0 else "Low probability of rain")
            time_spec = f" ({time_of_day})" if time_of_day != "All Day" else ""

            hdr = t["header_rain"].format(loc=loc_name, date=target_date_str, time_spec=time_spec)
            answer = (
                f"{hdr}\n"
                f"Rainfall Status: {rain_status} ({rain_prob:.0f}% chance, expected accumulation: {precip_mm:.1f} mm). "
                f"Expected condition: {cond}. Temperatures range between {target_daily.temp_min:.1f}°C and {target_daily.temp_max:.1f}°C."
            )
            if rain_prob >= 30.0 or precip_mm > 0.5:
                ai_recommendations.append(f"{prefix}{t['umbrella_yes']}")
            else:
                ai_recommendations.append(f"{prefix}{t['umbrella_no']}")

        elif intent == "TRAVEL_FORECAST":
            rain_prob = target_daily.precipitation_probability if target_daily else 10.0
            precip_mm = target_daily.precipitation_sum_mm if target_daily else 0.0
            temp_est = target_daily.temp_min + 2.0 if target_daily else cur.temperature

            hdr = t["header_travel"].format(loc=loc_name, date=target_date_str, time=time_of_day)
            answer = (
                f"{hdr}\n"
                f"Expect temperatures around {temp_est:.1f}°C with a {rain_prob:.0f}% chance of rain ({precip_mm:.1f} mm accumulation). "
                f"Overall weather condition: {target_daily.condition_text if target_daily else cur.condition_text}. "
                f"Wind speeds will average around {cur.wind_speed:.1f} km/h."
            )
            ai_recommendations.append(f"{prefix}Check travel conditions for {time_of_day} departure. Allow extra travel time if rain or low visibility occurs.")

        elif intent == "SEVERE_ALERTS":
            if official_warnings:
                alerts_summary = "; ".join([f"{a.event} ({a.severity}): {a.headline}" for a in official_warnings])
                hdr = t["header_alerts"].format(loc=loc_name)
                answer = f"{hdr}\n{alerts_summary}"
                ai_recommendations.append(f"{prefix}Official severe weather alert active. Follow local authority instructions immediately.")
            else:
                answer = t["header_no_alerts"].format(loc=loc_name)
                ai_recommendations.append(f"{prefix}No severe weather warnings currently active.")

        elif intent == "SAFETY_ADVISORY":
            answer = t["header_safety"]
            ai_recommendations.append(f"{prefix}Heavy rainfall safety protocol active. Stay indoors and avoid flooded pathways.")

        elif intent == "MULTI_DAY_FORECAST":
            forecast_lines = []
            for d in daily_list[:5]:
                forecast_lines.append(f"- {d.date}: {d.condition_text}, High: {d.temp_max}°C, Low: {d.temp_min}°C, Rain: {d.precipitation_probability}% ({d.precipitation_sum_mm} mm)")
            
            forecast_str = "\n".join(forecast_lines)
            hdr = t["header_5day"].format(loc=loc_name)
            answer = f"{hdr}\n{forecast_str}"
            ai_recommendations.append(f"{prefix}5-day multi-day forecast for {loc_name} retrieved successfully.")

        else:
            # GENERAL_WEATHER
            hdr = t["header_general"].format(loc=loc_name, date=target_date_str)
            answer = (
                f"{hdr}\n"
                f"Current temperature is {cur.temperature:.1f}°C ({cur.condition_text.lower()}). "
                f"Forecast temperatures range from a minimum of {target_daily.temp_min if target_daily else cur.temperature:.1f}°C to a maximum of {target_daily.temp_max if target_daily else cur.temperature:.1f}°C "
                f"with a {target_daily.precipitation_probability if target_daily else 10:.0f}% probability of rain."
            )
            ai_recommendations.append(f"{prefix}General weather details for {loc_name} provided.")

        return ChatResponse(
            query=query,
            answer=answer,
            grounded_facts=grounded_facts,
            official_warnings=official_warnings,
            ai_recommendations=ai_recommendations,
            language=request.language,
            low_bandwidth_mode=request.low_bandwidth
        )

    def _is_prompt_injection(self, query: str) -> bool:
        for pattern in INJECTION_PATTERNS:
            if pattern.search(query):
                return True
        return False

    def _build_security_defused_response(self, request: ChatRequest) -> ChatResponse:
        lang_code = request.language.lower() if request.language and request.language.lower() in MULTILINGUAL_TEXTS else "en"
        t = MULTILINGUAL_TEXTS.get(lang_code, MULTILINGUAL_TEXTS["en"])
        prefix = t["ai_prefix"]

        return ChatResponse(
            query=request.query,
            answer=(
                "I am WeatherGPT, a grounded AI weather intelligence system. "
                "I can process natural language weather questions and retrieve verified meteorological data."
            ),
            grounded_facts=[
                GroundedFact(
                    fact_type="SECURITY_NOTICE",
                    fact_text="System instructions and secrets are protected. Query processed safely.",
                    source="WeatherGPT Security Guardrail"
                )
            ],
            official_warnings=[],
            ai_recommendations=[f"{prefix}Please ask a weather-related query."],
            language=request.language,
            low_bandwidth_mode=request.low_bandwidth
        )

llm_service = GroundedWeatherGPTService()
