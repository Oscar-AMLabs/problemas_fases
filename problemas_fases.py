from flask import Flask, render_template
import requests
from datetime import timedelta
#teste
app = Flask(__name__)

def pipefy_send(query):
    url = "https://api.pipefy.com/graphql"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE2OTMzMTE3NTgsImp0aSI6ImE0OGU0MjIxLTE5ODMtNDgyOC1hY2E0LTk3M2FjMDgxYjljZiIsInN1YiI6MzAyNDg4MjU2LCJ1c2VyIjp7ImlkIjozMDI0ODgyNTYsImVtYWlsIjoiY2Fpby5wYWdsaWFyYW5pQGFtbGFicy5jb20uYnIiLCJhcHBsaWNhdGlvbiI6MzAwMjcxMjAyLCJzY29wZXMiOltdfSwiaW50ZXJmYWNlX3V1aWQiOm51bGx9.amWFG4ywllqfP7AK8tYwEZ-Z8LlCrnnOe6UBjHxhq3GGOX9n3c8CU3QIAPoCd-4vRIaY2p35Gndrn9oMFnAy5g"
    }
    response = requests.post(url, json={"query": query}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro na chamada da API do Pipefy: {response.status_code}\n\n")
        print(response.text)
        return None
    
def buscar_dados_pipefy_cards_atrasados(phase_id):
    query = f'''query {{
        phase(id: "{phase_id}") {{
            cards {{
                totalCount
                nodes {{
                    current_phase_age
                    id
                }}
            }}
        }}
    }}'''
    response = pipefy_send(query)
    if response and 'data' in response and 'phase' in response['data']:
        return response['data']['phase']['cards']['nodes']
    else:
        print("Erro ao buscar dados do Pipefy ou resposta inesperada.")
        return []

@app.route('/')
def problemas_fases():

    fases_P8 = {
        '00 - Configurar Card': '326468567',
        '2 - Aguardar Email P8': '321208431',
        '3 - Verificar Email P8': '321208483'
    }

    fases_E01 = {
        '0 - Configuração de Cards': '311259011',
        '02 - Cadastro no Omie': '311815660',
        '06 - Gerar Etiqueta': '311913416',
        '09 - Gerar contrato': '318519144',
        '12- Gerar Nota Fiscal': '311967060',
        '14 - Criar usuário SWAGGER': '311259012',
        '18 - Criar cards filho': '327697690'
    }

    fases_E02 = {
        '16 - Migração Rápida': '333112395',
        '21 - Desvio de Entrega': '321106741',
        'Criar Cards filho': '328358733'
    }

    fases_E03 = {
        '21 - Atualizar Omie': '311286224'
    }

    fases_TA = {
        'Migração Rápida':'333129186'
    }

    time_limits = {
        'P8': {
            '00 - Configurar Card': timedelta(hours=1),
            '2 - Aguardar Email P8': timedelta(days=2),
            '3 - Verificar Email P8': timedelta(hours=3)
        },
        'E01': {
            '0 - Configuração de Cards': timedelta(hours=1),
            '06 - Gerar Etiqueta': timedelta(hours=1),
            '12- Gerar Nota Fiscal': timedelta(hours=1),
            '18 - Criar cards filho': timedelta(hours=1),
            '02 - Cadastro no Omie': timedelta(hours=1),
            '09 - Gerar contrato': timedelta(hours=1),
            '14 - Criar usuário SWAGGER': timedelta(hours=1)
        },
        'E02': {
            'Criar Cards filho': timedelta(hours=1),
            '16 - Migração Rápida': timedelta(days=2),
            '21 - Desvio de Entrega': timedelta(days=2)
        },
        'E03': {
            '21 - Atualizar Omie': timedelta(hours=24)
        },
        'TA': {
            'Migração Rápida': timedelta(days=2)
        }
    }

    pipes = {
        'P8': fases_P8,
        'E01': fases_E01,
        'E02': fases_E02,
        'E03': fases_E03,
        'TA': fases_TA
    }

    stuck_cards = {
        'P8': [],
        'E01':[],
        'E02':[],
        'E03':[],
        'TA':[]
    }

    for pipe, fases in pipes.items():
        print(f"\nPipe: {pipe}, Fases: {fases}")

        for fase, fase_id in fases.items():

            print(f"\nPipe: {pipe}, Fase: {fase}, Fase ID: {fase_id}")
            cards = buscar_dados_pipefy_cards_atrasados(fase_id)

            if cards:

                for card in cards:

                    card_id = card['id']
                    print(f"\nCard ID: {card_id}")

                    current_phase_age_seconds = card['current_phase_age']
                    current_phase_age_timedelta = timedelta(seconds=current_phase_age_seconds)
                    print(f"\nTempo na Fase: {current_phase_age_timedelta}")

                    time_limit = time_limits[pipe][fase]
                    print(f"\nLimite de Tempo: {time_limit}")

                    if current_phase_age_timedelta > time_limit:

                        stuck_cards[pipe].append({
                            'phase': fase,
                            'time_in_phase': str(current_phase_age_timedelta),
                            'card_id': card_id
                        })
                        print(f"\nCard Atrasado: {stuck_cards[pipe]}")

    return render_template('problemas_fases.html', stuck_cards=stuck_cards)

if __name__ == '__main__':
    app.run(debug=True)
