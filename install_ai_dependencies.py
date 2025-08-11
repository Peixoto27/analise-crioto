#!/usr/bin/env python3
"""
Script para instalar dependências necessárias para o sistema de IA
"""

import subprocess
import sys

def install_package(package):
    """Instala um pacote Python"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado com sucesso")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Erro ao instalar {package}")
        return False

def main():
    print("🚀 Instalando dependências para o sistema de IA...")
    
    # Lista de pacotes necessários
    packages = [
        "scikit-learn>=1.0.0",
        "textblob>=0.17.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0"
    ]
    
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Resultado da instalação:")
    print(f"   ✅ Sucesso: {success_count}/{len(packages)}")
    print(f"   ❌ Falhas: {len(packages) - success_count}/{len(packages)}")
    
    if success_count == len(packages):
        print("\n🎉 Todas as dependências foram instaladas com sucesso!")
        print("🤖 O sistema de IA está pronto para uso!")
    else:
        print("\n⚠️ Algumas dependências falharam. Verifique os erros acima.")
    
    # Baixa dados do TextBlob se necessário
    try:
        import textblob
        print("\n📥 Baixando dados do TextBlob...")
        textblob.download_corpora.download_all()
        print("✅ Dados do TextBlob baixados com sucesso")
    except Exception as e:
        print(f"⚠️ Erro ao baixar dados do TextBlob: {e}")

if __name__ == "__main__":
    main()

