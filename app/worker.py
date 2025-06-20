import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from app.PullBDLoggi import atualizar_dados_loggi
from app.OrganizarBD import organizar_dados

while True:
    try:
        print("🔄 Atualizando dados da Loggi...")
        atualizar_dados_loggi()
        organizar_dados()
        print("✅ Atualização concluída.")
    except Exception as e:
        print(f"Erro: {e}")
    time.sleep(300)