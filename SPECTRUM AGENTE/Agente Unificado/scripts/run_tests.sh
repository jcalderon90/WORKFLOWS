#!/bin/bash

# Script helper para ejecutar los tests del Spectrum Agente
# Uso: ./scripts/run_tests.sh [opción]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir
print_menu() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Spectrum Agente - Test Suite Runner${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}\n"

    echo "Opciones:"
    echo -e "${GREEN}1${NC} — Test rápido (saludo_inicial) — 30 segundos"
    echo -e "${GREEN}2${NC} — Happy Path (conversación completa) — 3-5 minutos"
    echo -e "${GREEN}3${NC} — Test sin datos (valida lead_collector) — 30 segundos"
    echo -e "${GREEN}4${NC} — Test fuera de contexto (guardrail) — 30 segundos"
    echo -e "${GREEN}5${NC} — Test proyectos múltiples (ambigüedad) — 30 segundos"
    echo -e "${GREEN}6${NC} — Test RSVP (agendar cita) — 3-5 minutos"
    echo -e "${GREEN}7${NC} — Suite COMPLETA (todos los tests) — 8-10 minutos"
    echo -e "${GREEN}8${NC} — Listar todos los tests disponibles"
    echo -e "${GREEN}9${NC} — Ver documentación"
    echo -e "${GREEN}0${NC} — Salir\n"
}

run_test() {
    local scenario=$1
    local description=$2

    echo -e "\n${YELLOW}⏳ Ejecutando: ${description}${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}\n"

    cd "$PROJECT_ROOT"
    python3 scripts/test_agent.py --scenario "$scenario"
}

run_all_tests() {
    echo -e "\n${YELLOW}⏳ Ejecutando: SUITE COMPLETA (10 escenarios)${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}\n"

    cd "$PROJECT_ROOT"
    python3 scripts/test_agent.py
}

list_tests() {
    echo -e "\n${YELLOW}📋 Tests disponibles:${NC}\n"
    cd "$PROJECT_ROOT"
    python3 scripts/test_agent.py --list
}

show_docs() {
    echo -e "\n${BLUE}Documentación disponible:${NC}\n"
    echo "1. QUICK_START_TESTING.md — Guía rápida en 3 pasos"
    echo "2. scripts/README_TEST_AGENT.md — Documentación completa"
    echo "3. TEST_SUITE_COMPLETE.md — Detalles técnicos y casos de uso\n"

    read -p "¿Cuál quieres leer? (1-3) [Enter para salir]: " doc_choice

    case $doc_choice in
        1)
            if command -v cat &> /dev/null; then
                cd "$PROJECT_ROOT"
                cat QUICK_START_TESTING.md | less
            fi
            ;;
        2)
            if command -v cat &> /dev/null; then
                cd "$PROJECT_ROOT"
                cat scripts/README_TEST_AGENT.md | less
            fi
            ;;
        3)
            if command -v cat &> /dev/null; then
                cd "$PROJECT_ROOT"
                cat TEST_SUITE_COMPLETE.md | less
            fi
            ;;
        *)
            echo "Cancelado."
            ;;
    esac
}

# Main
if [ -z "$1" ]; then
    while true; do
        print_menu
        read -p "Elige una opción (0-9): " choice

        case $choice in
            1)
                run_test "saludo_inicial" "Test rápido (saludo)"
                ;;
            2)
                run_test "happy_path_completo" "Happy Path completo"
                ;;
            3)
                run_test "lead_sin_datos" "Test sin datos"
                ;;
            4)
                run_test "fuera_de_contexto" "Test guardrail"
                ;;
            5)
                run_test "multiples_proyectos" "Test ambigüedad"
                ;;
            6)
                run_test "rsvp_flow" "Test RSVP"
                ;;
            7)
                run_all_tests
                ;;
            8)
                list_tests
                ;;
            9)
                show_docs
                ;;
            0)
                echo -e "\n${GREEN}¡Hasta luego!${NC}\n"
                exit 0
                ;;
            *)
                echo -e "\n${YELLOW}Opción inválida. Intenta de nuevo.${NC}"
                ;;
        esac

        read -p "¿Correr otro test? (S/n): " again
        if [[ ! $again =~ ^[Ss]$ ]]; then
            echo -e "\n${GREEN}¡Hasta luego!${NC}\n"
            exit 0
        fi
    done
else
    # Si se pasa un argumento, ejecutar directamente
    case $1 in
        quick)
            run_test "saludo_inicial" "Test rápido"
            ;;
        happy)
            run_test "happy_path_completo" "Happy Path"
            ;;
        all)
            run_all_tests
            ;;
        list)
            list_tests
            ;;
        *)
            echo "Uso: $0 [quick|happy|all|list]"
            echo ""
            echo "O ejecuta sin argumentos para menú interactivo:"
            echo "  $0"
            ;;
    esac
fi
