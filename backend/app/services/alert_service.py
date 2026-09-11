from datetime import datetime, timezone
from typing import List, Dict, Any, Union, Optional
from app.schemas.alerts import (
    WeatherHazardType,
    RiskContributingFactor,
    WeatherGPTCalculatedRisk,
    OfficialMeteorologicalWarning,
    AIGeneratedAdvisory,
    LocationRiskFactors,
    WeatherRiskInput,
    WeatherRiskEvaluationResponse
)
from app.schemas.weather import SevereWeatherAlert, CurrentWeather
from app.core.logging import logger


class AlertRiskEngine:
    """
    WeatherGPT Transparent Severe Weather Risk Assessment & Emergency Advisory Engine.
    Evaluates meteorological thresholds against WMO risk standards, model forecast uncertainty,
    official warnings, and location-specific risk factors.
    """

    @staticmethod
    def evaluate_weather_risk(risk_input: WeatherRiskInput) -> WeatherGPTCalculatedRisk:
        """
        Calculates an explainable Weather Impact Score from 0 to 100 based on multi-factor analysis:
        1. Rainfall (precipitation rate/accumulation)
        2. Wind & Cyclone intensity
        3. Temperature (Heatwave / Extreme Heat Index / Deep Freeze)
        4. Convective Weather Code / Thunderstorm / UV Radiation
        5. Official Meteorological Warnings presence
        6. Location-specific vulnerability factors
        7. Forecast uncertainty safety margin
        """
        contributing_factors: List[RiskContributingFactor] = []
        detected_hazards: List[WeatherHazardType] = []

        # 1. Rainfall Factor (Max 50 pts)
        precip = risk_input.precipitation_mm_hr
        precip_score = 0.0
        precip_desc = "Normal precipitation level."
        if precip >= 30.0:
            precip_score = 50.0
            precip_desc = f"Torrential rainfall ({precip:.1f} mm/h) creating flash flood & inundation hazards."
            detected_hazards.append(WeatherHazardType.HEAVY_RAINFALL)
            detected_hazards.append(WeatherHazardType.FLOOD_RISK)
        elif precip >= 15.0:
            precip_score = 30.0
            precip_desc = f"Heavy rainfall ({precip:.1f} mm/h) exceeding drainage capacity."
            detected_hazards.append(WeatherHazardType.HEAVY_RAINFALL)
        elif precip >= 5.0:
            precip_score = 15.0
            precip_desc = f"Moderate rain ({precip:.1f} mm/h)."
        elif precip > 0.0:
            precip_score = 5.0
            precip_desc = f"Light rain ({precip:.1f} mm/h)."

        contributing_factors.append(RiskContributingFactor(
            factor_name="rainfall",
            score_contribution=round(precip_score, 1),
            weight=0.25,
            raw_value=f"{precip:.1f} mm/h",
            description=precip_desc
        ))

        # 2. Wind & Cyclone Factor (Max 70 pts for Cyclone)
        wind = risk_input.wind_speed
        gust = risk_input.wind_gust or wind
        pressure = risk_input.pressure
        wind_score = 0.0
        wind_desc = "Normal wind speed."

        if pressure <= 995.0 and (wind >= 70.0 or gust >= 90.0):
            wind_score = 70.0
            wind_desc = f"Severe tropical cyclone/hurricane conditions (Pressure {pressure:.1f} hPa, Wind {wind:.1f} km/h, Gusts {gust:.1f} km/h)."
            detected_hazards.append(WeatherHazardType.CYCLONE)
            detected_hazards.append(WeatherHazardType.STRONG_WIND)
        elif wind >= 90.0 or gust >= 110.0:
            wind_score = 55.0
            wind_desc = f"Extreme storm-force winds ({wind:.1f} km/h, Gusts {gust:.1f} km/h) capable of structural damage."
            detected_hazards.append(WeatherHazardType.STRONG_WIND)
        elif wind >= 75.0 or gust >= 90.0:
            wind_score = 35.0
            wind_desc = f"Severe high wind danger ({wind:.1f} km/h)."
            detected_hazards.append(WeatherHazardType.STRONG_WIND)
        elif wind >= 50.0 or gust >= 70.0:
            wind_score = 22.0
            wind_desc = f"Strong wind hazard ({wind:.1f} km/h)."
            detected_hazards.append(WeatherHazardType.STRONG_WIND)
        elif wind >= 35.0 or gust >= 50.0:
            wind_score = 12.0
            wind_desc = f"Strong wind gusts ({wind:.1f} km/h)."
            if WeatherHazardType.STRONG_WIND not in detected_hazards:
                detected_hazards.append(WeatherHazardType.STRONG_WIND)
        elif wind > 20.0:
            wind_score = 5.0
            wind_desc = f"Moderate breeze ({wind:.1f} km/h)."

        contributing_factors.append(RiskContributingFactor(
            factor_name="wind",
            score_contribution=round(wind_score, 1),
            weight=0.25,
            raw_value=f"{wind:.1f} km/h (Gust: {gust:.1f} km/h, Pressure: {pressure:.1f} hPa)",
            description=wind_desc
        ))

        # 3. Temperature & Heatwave / Deep Freeze Factor (Max 70 pts for Extreme Heatwave/Freeze)
        temp = risk_input.temperature
        humidity = risk_input.humidity
        app_temp = risk_input.apparent_temperature
        if app_temp is None:
            if temp > 27.0 and humidity > 40:
                app_temp = temp + (0.55 * (1 - humidity / 100.0) * (temp - 14.0))
            else:
                app_temp = temp

        temp_score = 0.0
        temp_desc = "Thermal comfort within safe standard bounds."

        if temp >= 42.0 or app_temp >= 48.0 or (temp >= 40.0 and humidity >= 60.0):
            temp_score = 70.0
            temp_desc = f"Extreme Heatwave & Dangerous Heat Index Hazard (Temp {temp:.1f}°C, Heat Index {app_temp:.1f}°C, Humidity {humidity:.0f}%)."
            detected_hazards.append(WeatherHazardType.HEATWAVE)
        elif temp >= 38.0 or app_temp >= 42.0:
            temp_score = 48.0
            temp_desc = f"Severe Heatwave conditions (Temp {temp:.1f}°C, Heat Index {app_temp:.1f}°C)."
            detected_hazards.append(WeatherHazardType.HEATWAVE)
        elif temp >= 35.0 or (temp >= 32.0 and humidity >= 75.0):
            temp_score = 25.0
            temp_desc = f"Moderate Heat Warning (Temp {temp:.1f}°C, Humidity {humidity:.0f}%)."
            if WeatherHazardType.HEATWAVE not in detected_hazards:
                detected_hazards.append(WeatherHazardType.HEATWAVE)
        elif temp <= -20.0:
            temp_score = 70.0
            temp_desc = f"Extreme Deep Freeze ({temp:.1f}°C) posing severe frostbite risk."
            detected_hazards.append(WeatherHazardType.BLIZZARD_DEEP_FREEZE)
        elif temp <= -10.0:
            temp_score = 48.0
            temp_desc = f"Severe Deep Freeze ({temp:.1f}°C)."
            detected_hazards.append(WeatherHazardType.BLIZZARD_DEEP_FREEZE)

        contributing_factors.append(RiskContributingFactor(
            factor_name="temperature",
            score_contribution=round(temp_score, 1),
            weight=0.20,
            raw_value=f"Temp: {temp:.1f}°C, Feels like: {app_temp:.1f}°C, Humidity: {humidity:.0f}%",
            description=temp_desc
        ))

        # 4. WMO Convective Weather Code & Thunderstorm Factor (Max 25 pts)
        code_score = 0.0
        code_desc = "Normal atmospheric conditions."
        if risk_input.weather_code in (96, 99):
            code_score = 25.0
            code_desc = "Severe Thunderstorm with Heavy Hail hazard."
            if WeatherHazardType.THUNDERSTORM not in detected_hazards:
                detected_hazards.append(WeatherHazardType.THUNDERSTORM)
        elif risk_input.weather_code == 95:
            code_score = 20.0
            code_desc = "Active Thunderstorm with Lightning hazard."
            if WeatherHazardType.THUNDERSTORM not in detected_hazards:
                detected_hazards.append(WeatherHazardType.THUNDERSTORM)
        elif risk_input.weather_code in (65, 82):
            code_score = 15.0
            code_desc = "Torrential Rain Shower hazard."
            if WeatherHazardType.HEAVY_RAINFALL not in detected_hazards:
                detected_hazards.append(WeatherHazardType.HEAVY_RAINFALL)

        contributing_factors.append(RiskContributingFactor(
            factor_name="thunderstorm_convective",
            score_contribution=round(code_score, 1),
            weight=0.15,
            raw_value=f"WMO Weather Code {risk_input.weather_code}",
            description=code_desc
        ))

        # 5. Official Meteorological Warning Factor (Max 25 pts)
        official_alerts = risk_input.official_alerts or []
        official_score = 0.0
        official_desc = "No official meteorological warnings currently active."
        if official_alerts:
            if any(a.severity.upper() == "EXTREME" for a in official_alerts):
                official_score = 25.0
                official_desc = f"Extreme Official Meteorological Warning in effect ({len(official_alerts)} warning(s))."
            elif any(a.severity.upper() in ("SEVERE", "HIGH") for a in official_alerts):
                official_score = 18.0
                official_desc = f"Severe Official Meteorological Warning in effect ({len(official_alerts)} warning(s))."
            else:
                official_score = 10.0
                official_desc = f"Moderate Official Meteorological Warning in effect ({len(official_alerts)} warning(s))."
            
            if WeatherHazardType.OTHER_OFFICIAL_WARNING not in detected_hazards:
                detected_hazards.append(WeatherHazardType.OTHER_OFFICIAL_WARNING)

        contributing_factors.append(RiskContributingFactor(
            factor_name="official_warning",
            score_contribution=round(official_score, 1),
            weight=0.15,
            raw_value=f"{len(official_alerts)} active warning(s)",
            description=official_desc
        ))

        # 6. Location-Specific Risk Factors (Max 15 pts)
        loc = risk_input.location_factors or LocationRiskFactors()
        loc_score = 0.0
        loc_reasons = []

        if loc.is_flood_prone or (loc.soil_saturation_pct and loc.soil_saturation_pct > 70.0):
            loc_score += 6.0
            loc_reasons.append("Flood-prone river basin/saturated ground")
            if WeatherHazardType.FLOOD_RISK not in detected_hazards and precip > 10.0:
                detected_hazards.append(WeatherHazardType.FLOOD_RISK)
        if loc.is_coastal or (loc.elevation_meters is not None and loc.elevation_meters < 10.0):
            loc_score += 6.0
            loc_reasons.append("Low-lying coastal storm surge zone")
        if loc.is_urban_dense and WeatherHazardType.HEATWAVE in detected_hazards:
            loc_score += 3.0
            loc_reasons.append("Dense urban heat island effect")

        loc_score = min(loc_score, 15.0)
        loc_desc = ", ".join(loc_reasons) if loc_reasons else "Standard baseline geography."

        contributing_factors.append(RiskContributingFactor(
            factor_name="location_risk",
            score_contribution=round(loc_score, 1),
            weight=0.10,
            raw_value=f"Coastal={loc.is_coastal}, FloodProne={loc.is_flood_prone}, Elev={loc.elevation_meters}m",
            description=loc_desc
        ))

        # 7. Forecast Uncertainty Factor (Max 10 pts)
        uncert = risk_input.forecast_uncertainty
        uncert_score = round(uncert * 10.0, 1)
        uncert_desc = f"Low forecast uncertainty margin ({uncert * 100:.0f}% spread)." if uncert < 0.3 else f"Higher forecast model variance ({uncert * 100:.0f}% spread) adding conservative safety score buffer."

        contributing_factors.append(RiskContributingFactor(
            factor_name="forecast_uncertainty",
            score_contribution=round(uncert_score, 1),
            weight=0.05,
            raw_value=f"{uncert * 100:.1f}% variance",
            description=uncert_desc
        ))

        # Total score computation & clamping strictly between 0 and 100
        raw_total = sum(f.score_contribution for f in contributing_factors)
        final_score = round(min(max(raw_total, 0.0), 100.0), 1)

        # Severity Classification
        if final_score >= 70.0:
            severity = "EXTREME"
        elif final_score >= 45.0:
            severity = "HIGH"
        elif final_score >= 20.0:
            severity = "MODERATE"
        else:
            severity = "MINIMAL"

        now_iso = datetime.now(timezone.utc).isoformat()

        return WeatherGPTCalculatedRisk(
            risk_score=final_score,
            severity=severity,
            contributing_factors=contributing_factors,
            detected_hazards=list(set(detected_hazards)),
            timestamp=now_iso,
            source="WeatherGPT Risk Engine v1.0",
            is_official_warning=False
        )

    @staticmethod
    def generate_ai_advisory(
        calculated_risk: WeatherGPTCalculatedRisk,
        official_warnings: List[OfficialMeteorologicalWarning],
        location_name: str
    ) -> AIGeneratedAdvisory:
        """
        Generates structured AI-generated safety guidance based on risk assessment.
        Ensures clear non-official designation.
        """
        actions = []
        if calculated_risk.severity == "EXTREME":
            advisory = f"CRITICAL WEATHER SAFETY ALERT for {location_name}: High risk weather pattern detected. Avoid all unnecessary travel and secure emergency supplies."
            actions.extend([
                "Monitor official emergency management broadcasts.",
                "Charge mobile devices and prepare emergency disaster kits.",
                "Seek indoor shelter away from windows."
            ])
        elif calculated_risk.severity == "HIGH":
            advisory = f"HIGH WEATHER ADVISORY for {location_name}: Significant weather hazards present. Exercise heightened caution outdoors."
            actions.extend([
                "Secure loose outdoor objects.",
                "Limit prolonged exposure to severe temperature/wind.",
                "Check local transportation advisories."
            ])
        elif calculated_risk.severity == "MODERATE":
            advisory = f"MODERATE WEATHER ADVISORY for {location_name}: Elevated weather risk present. Stay alert to changing conditions."
            actions.append("Keep umbrella/weather gear accessible.")
        else:
            advisory = f"Baseline normal weather conditions in {location_name}. Standard outdoor activities permitted."
            actions.append("No immediate severe weather protective action required.")

        now_iso = datetime.now(timezone.utc).isoformat()
        return AIGeneratedAdvisory(
            advisory_text=advisory,
            recommended_actions=actions,
            confidence_level="HIGH",
            timestamp=now_iso,
            source="WeatherGPT AI Advisory Service",
            is_official_warning=False
        )

    @staticmethod
    def calculate_risk_score(current: CurrentWeather) -> Dict[str, Any]:
        """
        Legacy adapter method for backwards compatibility with existing endpoints and tests.
        """
        risk_input = WeatherRiskInput(
            latitude=0.0,
            longitude=0.0,
            temperature=current.temperature,
            apparent_temperature=current.apparent_temperature,
            humidity=current.humidity,
            pressure=current.pressure,
            wind_speed=current.wind_speed,
            weather_code=current.weather_code
        )
        calculated = AlertRiskEngine.evaluate_weather_risk(risk_input)

        reasons = []
        for factor in calculated.contributing_factors:
            if factor.score_contribution > 0:
                reasons.append(f"{factor.factor_name.title()}: {factor.description}")

        return {
            "risk_score": calculated.risk_score,
            "risk_level": calculated.severity,
            "hazards": reasons
        }

    @staticmethod
    def filter_official_warnings(alerts: List[SevereWeatherAlert]) -> List[SevereWeatherAlert]:
        """Ensures non-official alerts are excluded from official warning badges."""
        return [a for a in alerts if a.is_official_warning]


alert_engine = AlertRiskEngine()
