import os
import boto3
import psycopg2
import csv
import io
from dotenv import load_dotenv

# Carrega as credenciais do seu arquivo .env
load_dotenv()

s3 = boto3.client("s3")

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )

def process_file(bucket, key):
    if not key.endswith(".csv"):
        return

    print(f"Lendo: {key}...")
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    
    conn = get_db_connection()
    cur = conn.cursor()

    # Identifica a tabela e a coluna de categoria (Rede ou Faculdade)
    if "video_views_dia_rede_social" in key:
        table = "gold_video_views_dia_rede_social"
        col = "rede_social"
    else:
        table = "gold_video_views_dia_faculdade"
        col = "faculdade"

    # Lógica de UPSERT: Se a data e a categoria já existirem, ele atualiza os números
    upsert_sql = f"""
        INSERT INTO {table} (data_postagem, {col}, total_views, total_likes, total_comentarios, total_videos)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (data_postagem, {col}) 
        DO UPDATE SET 
            total_views = EXCLUDED.total_views,
            total_likes = EXCLUDED.total_likes,
            total_comentarios = EXCLUDED.total_comentarios,
            total_videos = EXCLUDED.total_videos;
    """

    for row in reader:
        cur.execute(upsert_sql, (
            row['data_postagem'], row[col], 
            int(row['total_views']), int(row['total_likes']), 
            int(row['total_comentarios']), int(row['total_videos'])
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Finalizado: {table}")

# Para rodar o BACKFILL (Carga de todos os arquivos atuais)
def full_load():
    bucket_name = "capstone-impacta"
    prefix = "Capstone/gold/"
    
    # Lista todos os arquivos na pasta gold
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        if "Contents" in page:
            for obj in page["Contents"]:
                process_file(bucket_name, obj["Key"])

if __name__ == "__main__":
    full_load()
