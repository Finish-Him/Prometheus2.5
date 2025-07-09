"""
Script para criar um logo simples para o Oráculo 4.0
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Criar diretório para arquivos estáticos se não existir
os.makedirs("/home/ubuntu/projeto_integracao_manus/static", exist_ok=True)

# Criar uma imagem com fundo preto
img = Image.new('RGB', (200, 200), color=(0, 0, 0))
d = ImageDraw.Draw(img)

# Desenhar um círculo azul
d.ellipse((50, 50, 150, 150), fill=(0, 100, 255))

# Adicionar texto "O 4.0" no centro
try:
    # Tentar usar uma fonte do sistema
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
except:
    # Fallback para fonte padrão
    font = ImageFont.load_default()

d.text((70, 85), "O 4.0", fill=(255, 255, 255), font=font)

# Salvar a imagem
img.save("/home/ubuntu/projeto_integracao_manus/static/logo.png")

print("Logo criado com sucesso em /home/ubuntu/projeto_integracao_manus/static/logo.png")
