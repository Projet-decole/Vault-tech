# Image Hadoop officielle + un dossier de stockage appartenant à l'utilisateur "hadoop".
# Sans ça, le volume Docker monté sur /hadoop/dfs appartiendrait à root et HDFS ne pourrait pas y écrire.
FROM apache/hadoop:3.4.3

USER root
RUN mkdir -p /hadoop/dfs && chown hadoop:users /hadoop/dfs
USER hadoop
