FROM postgres:latest

# 设置环境变量
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=payment_db

# 暴露PostgreSQL默认端口
EXPOSE 5432

# 创建数据目录
VOLUME ["/var/lib/postgresql/data"] 