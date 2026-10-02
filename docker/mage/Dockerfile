# Image Mage officielle + ce dont nos blocs ont besoin.
#   phase 3 : client WebHDFS
#   phase 4 : Java + pyspark (Mage = "driver" Spark)
#   (dbt-postgres est déjà inclus dans l'image Mage)
FROM mageai/mageai:0.9.79

# Spark est écrit en Java/Scala : le driver a besoin d'une JVM.
# Java 17 = même version que les conteneurs spark-master / spark-worker.
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# hdfs = client Python qui parle à HDFS via WebHDFS (HTTP, port 9870)
RUN pip install --no-cache-dir hdfs==2.7.3

# pyspark dans un environnement Python SÉPARÉ (virtualenv), et pas dans celui de Mage :
# si Mage voit pyspark, il ouvre une session Spark locale à chaque passage de données
# entre blocs (ingestion : 23 s → 8 min). Nos blocs appellent /opt/pyspark/bin/spark-submit.
# pyspark DOIT être à la version exacte du cluster (apache/spark:4.1.3).
RUN python -m venv /opt/pyspark \
    && /opt/pyspark/bin/pip install --no-cache-dir pyspark==4.1.3
