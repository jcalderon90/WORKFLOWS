#!/usr/bin/env python3
"""
Test Suite para Spectrum Agente Unificado
==========================================

Script para simular conversaciones completas con el agente Sof-IA,
como si fuera un cliente real en WhatsApp/Instagram/Messenger.

Uso:
    python3 scripts/test_agent.py                    # Ejecuta todos los escenarios
    python3 scripts/test_agent.py --scenario saludo_inicial
    python3 scripts/test_agent.py --list              # Lista los escenarios
    python3 scripts/test_agent.py --canal instagram   # Prueba con canal específico

Requerimientos:
    - Python 3.6+
    - Solo bibliotecas estándar (urllib, json, time, uuid, sys, argparse)
"""

import json
import urllib.request
import urllib.error
import time
import uuid
import sys
import argparse
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

WEBHOOK_URL = "https://agentsprod.redtec.ai/webhook/spectrum-agent"
TIMEOUT_SECONDS = 35  # 10s wait en flujo + 20s IA + 5s margen
DEFAULT_PHONE = "+50212345678"
DEFAULT_PAGE_ID = "page_spectrum_test"

# Colores ANSI para output
COLOR_HEADER = "\033[94m"  # Azul
COLOR_OK = "\033[92m"      # Verde
COLOR_ERROR = "\033[91m"   # Rojo
COLOR_WARN = "\033[93m"    # Amarillo
COLOR_INFO = "\033[96m"    # Cyan
COLOR_RESET = "\033[0m"

# ============================================================================
# ESCENARIOS DE PRUEBA
# ============================================================================

TEST_SCENARIOS = {
    "saludo_inicial": {
        "description": "Validar bienvenida sin datos previos",
        "canal": "WhatsApp",
        "messages": [
            {"text": "Hola", "validate": ["Sof-IA", "ayudarte"]},
        ]
    },

    "happy_path_completo": {
        "description": "Conversación completa: saludo → datos → proyecto → consulta → cita",
        "canal": "WhatsApp",
        "messages": [
            {
                "text": "Hola, me interesa saber sobre los proyectos de Spectrum",
                "validate": ["proyecto", "Spectrum"]
            },
            {
                "text": "Mi nombre es Juan Pérez, correo: juan@example.com, teléfono: +50299999999",
                "validate": ["gracias", "Juan"]
            },
            {
                "text": "Me interesa Parque Vista Verde",
                "validate": ["PVV", "Vista Verde"]
            },
            {
                "text": "¿Cuántos metros cuadrados tiene?",
                "validate": []  # Depende de KB_SEARCH
            },
        ]
    },

    "lead_sin_datos": {
        "description": "Verifica que se llame lead_collector cuando faltan datos",
        "canal": "WhatsApp",
        "messages": [
            {
                "text": "¿Cuánto cuesta Parque Portales?",
                "validate": ["nombre", "correo", "teléfono", "datos"]  # Debe pedir datos
            },
        ]
    },

    "fuera_de_contexto": {
        "description": "Verifica el guardrail para temas ajenos a inmobiliaria",
        "canal": "WhatsApp",
        "messages": [
            {
                "text": "¿Cómo hago un programa en Python?",
                "validate": ["especializada", "proyectos", "vivienda"]
            },
        ]
    },

    "mencion_proyecto_directo": {
        "description": "Usuario menciona proyecto en primer mensaje",
        "canal": "WhatsApp",
        "messages": [
            {
                "text": "Hola, quiero saber todo sobre Parque Mariscal",
                "validate": ["Mariscal", "proyecto"]
            },
        ]
    },

    "solicita_asesoria": {
        "description": "Usuario solicita hablar con un asesor humano",
        "canal": "WhatsApp",
        "messages": [
            {
                "text": "Hola, necesito hablar con alguien",
                "validate": []
            },
            {
                "text": "Quiero que me contacte un asesor",
                "validate": ["asesor", "humano"]
            },
        ]
    },

    "multiples_proyectos": {
        "description": "Usuario pregunta por zona ambigua (Zona 15 = PVV o PSB)",
        "canal": "WhatsApp",
        "messages": [
            {
                "text": "¿Qué proyectos tienen en Zona 15?",
                "validate": ["Vista Verde", "Sotobosque"]
            },
        ]
    },

    "canal_instagram": {
        "description": "Prueba con canal Instagram",
        "canal": "Instagram",
        "messages": [
            {
                "text": "Hola, ¿tienes info de los apartamentos?",
                "validate": ["proyectos", "Spectrum"]
            },
        ]
    },

    "rsvp_flow": {
        "description": "Usuario quiere agendar una visita (RSVP)",
        "canal": "WhatsApp",
        "messages": [
            {
                "text": "Hola, me interesa agendar un tour",
                "validate": []
            },
            {
                "text": "Quiero visitar Parque Vista Verde",
                "validate": []
            },
            {
                "text": "Sí, quiero agendar para el sábado",
                "validate": ["fecha", "hora", "cita"]
            },
        ]
    },

    "modismos_guatemaltecos": {
        "description": "Usuario responde con modismos: simón, va, nel",
        "canal": "WhatsApp",
        "messages": [
            {
                "text": "Hola",
                "validate": []
            },
            {
                "text": "Simón, me interesa",
                "validate": []
            },
            {
                "text": "Vista Verde",
                "validate": []
            },
            {
                "text": "Nel, no me interesa ese precio",
                "validate": []
            },
        ]
    },
}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def generate_user_id():
    """Genera un user_id único para esta sesión de prueba."""
    return f"test_{uuid.uuid4().hex[:8]}"


def build_payload(user_id, message_text, canal="WhatsApp", page_id=DEFAULT_PAGE_ID, phone=DEFAULT_PHONE):
    """Construye el payload JSON que espera el webhook."""
    return {
        "key": user_id,
        "body": {
            "id": user_id,
            "page_id": page_id,
            "custom_fields": {
                "canal_ingreso": canal,
                "proyecto_interes": ""
            },
            "last_input_text": message_text,
            "whatsapp_phone": phone
        }
    }


def send_message(user_id, message_text, canal="WhatsApp"):
    """Envía un mensaje al webhook y retorna la respuesta."""
    payload = build_payload(user_id, message_text, canal)

    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        WEBHOOK_URL,
        data=data,
        headers=headers,
        method='POST'
    )

    try:
        start_time = time.time()
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
        elapsed = (time.time() - start_time) * 1000  # milisegundos

        response_data = response.read().decode('utf-8')

        # Intenta parsear como JSON
        try:
            response_json = json.loads(response_data) if response_data else {}
        except json.JSONDecodeError:
            response_json = {"raw": response_data}

        return {
            "success": True,
            "status_code": response.status,
            "elapsed_ms": int(elapsed),
            "data": response_json
        }

    except urllib.error.HTTPError as e:
        response_data = e.read().decode('utf-8')
        try:
            response_json = json.loads(response_data)
        except:
            response_json = {"error": response_data}

        return {
            "success": False,
            "status_code": e.code,
            "elapsed_ms": int((time.time() - start_time) * 1000),
            "data": response_json
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsed_ms": int((time.time() - start_time) * 1000)
        }


def validate_response(response_data, expected_keywords):
    """Valida si la respuesta contiene palabras clave esperadas."""
    if not expected_keywords:
        return None  # Sin validación específica

    response_text = json.dumps(response_data).lower()

    found = []
    missing = []

    for keyword in expected_keywords:
        if keyword.lower() in response_text:
            found.append(keyword)
        else:
            missing.append(keyword)

    return {
        "passed": len(missing) == 0,
        "found": found,
        "missing": missing
    }


def print_header(text):
    """Imprime un encabezado."""
    print(f"\n{COLOR_HEADER}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{COLOR_RESET}\n")


def print_turn(turn_num, total_turns, message_text, response, elapsed_ms, validation):
    """Imprime un turno de la conversación."""
    status_icon = f"{COLOR_OK}✅{COLOR_RESET}" if response["success"] else f"{COLOR_ERROR}❌{COLOR_RESET}"

    print(f"{status_icon} [{turn_num}/{total_turns}] Usuario: \"{message_text}\"")
    print(f"   Respuesta ({elapsed_ms}ms):")

    if response["success"]:
        data = response.get("data", {})

        # Extrae campos importantes si es un JSON válido
        if isinstance(data, dict):
            respuesta = data.get("respuesta", "")
            accion = data.get("accion", {})
            tools = data.get("depuracion", {}).get("herramientas_usadas", [])

            if respuesta:
                print(f"      {COLOR_INFO}respuesta{COLOR_RESET}: {respuesta[:100]}{'...' if len(respuesta) > 100 else ''}")
            if isinstance(accion, dict):
                print(f"      {COLOR_INFO}accion{COLOR_RESET}: {accion.get('tipo', 'desconocida')}")
            if tools:
                print(f"      {COLOR_INFO}tools{COLOR_RESET}: {', '.join(tools)}")
        else:
            print(f"      {data}")

        # Validación
        if validation:
            if validation["passed"]:
                print(f"   {COLOR_OK}✓ Validación pasada{COLOR_RESET} (encontradas: {', '.join(validation['found'])})")
            else:
                print(f"   {COLOR_WARN}⚠ Validación parcial{COLOR_RESET}")
                print(f"      Encontradas: {validation['found'] or 'ninguna'}")
                print(f"      Faltaban: {validation['missing']}")
    else:
        error = response.get("error", f"HTTP {response.get('status_code', 'unknown')}")
        print(f"      {COLOR_ERROR}Error: {error}{COLOR_RESET}")

    print()


def run_scenario(scenario_name, scenario_config, verbose=False):
    """Ejecuta un escenario de prueba completo."""
    print_header(f"ESCENARIO: {scenario_name}")
    print(f"Descripción: {scenario_config['description']}")
    print(f"Canal: {scenario_config['canal']}\n")

    user_id = generate_user_id()
    print(f"User ID (sesión): {COLOR_INFO}{user_id}{COLOR_RESET}\n")

    messages = scenario_config.get("messages", [])
    canal = scenario_config.get("canal", "WhatsApp")

    passed = 0
    failed = 0

    for idx, msg_config in enumerate(messages, 1):
        message_text = msg_config.get("text", "")
        expected_keywords = msg_config.get("validate", [])

        # Envía mensaje
        response = send_message(user_id, message_text, canal)
        elapsed_ms = response.get("elapsed_ms", 0)

        # Valida respuesta
        validation = validate_response(response.get("data", {}), expected_keywords)

        # Imprime turno
        print_turn(idx, len(messages), message_text, response, elapsed_ms, validation)

        # Tracking
        if response["success"]:
            if validation is None or validation["passed"]:
                passed += 1
            else:
                failed += 1
        else:
            failed += 1

        # Pequeña pausa entre mensajes (para no sobrecargar el sistema)
        if idx < len(messages):
            time.sleep(2)

    # Resumen
    print(f"\n{COLOR_HEADER}{'='*70}")
    print(f"RESUMEN: {COLOR_OK}{passed} pasados{COLOR_RESET}, {COLOR_ERROR}{failed} fallidos{COLOR_RESET}")
    print(f"{'='*70}{COLOR_RESET}\n")

    return {"passed": passed, "failed": failed}


def list_scenarios():
    """Lista todos los escenarios disponibles."""
    print(f"\n{COLOR_HEADER}Escenarios disponibles:{COLOR_RESET}\n")
    for name, config in TEST_SCENARIOS.items():
        print(f"  {COLOR_OK}•{COLOR_RESET} {name:30} — {config['description']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Test suite para Spectrum Agente Unificado",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 scripts/test_agent.py                    # Ejecuta todos los escenarios
  python3 scripts/test_agent.py --scenario saludo_inicial  # Un escenario específico
  python3 scripts/test_agent.py --list              # Lista los escenarios
  python3 scripts/test_agent.py --scenario happy_path_completo --verbose
        """
    )

    parser.add_argument(
        "--scenario",
        type=str,
        help="Ejecuta un escenario específico por nombre"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista todos los escenarios disponibles"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verbose (más detalles en output)"
    )

    args = parser.parse_args()

    if args.list:
        list_scenarios()
        return

    # Ejecuta escenarios
    total_passed = 0
    total_failed = 0

    if args.scenario:
        if args.scenario not in TEST_SCENARIOS:
            print(f"{COLOR_ERROR}Error: Escenario '{args.scenario}' no encontrado{COLOR_RESET}")
            print(f"Usa --list para ver los escenarios disponibles")
            sys.exit(1)

        results = run_scenario(args.scenario, TEST_SCENARIOS[args.scenario], args.verbose)
        total_passed += results["passed"]
        total_failed += results["failed"]
    else:
        # Ejecuta todos
        print(f"\n{COLOR_HEADER}🚀 Iniciando test suite completa ({len(TEST_SCENARIOS)} escenarios){COLOR_RESET}\n")

        for scenario_name, scenario_config in TEST_SCENARIOS.items():
            results = run_scenario(scenario_name, scenario_config, args.verbose)
            total_passed += results["passed"]
            total_failed += results["failed"]
            time.sleep(3)  # Pausa entre escenarios

    # Resumen final
    print(f"\n{COLOR_HEADER}{'='*70}")
    print(f"RESUMEN FINAL")
    print(f"{'='*70}{COLOR_RESET}")
    print(f"Total de mensajes: {total_passed + total_failed}")
    print(f"Pasados: {COLOR_OK}{total_passed}{COLOR_RESET}")
    print(f"Fallidos: {COLOR_ERROR}{total_failed}{COLOR_RESET}")

    if total_failed == 0:
        print(f"\n{COLOR_OK}✅ Todos los tests pasaron correctamente{COLOR_RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{COLOR_ERROR}❌ Algunos tests fallaron{COLOR_RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
