# 0.0.0.0 means it's available from all network interfaces in container
bind = "0.0.0.0:8000"

worker_class = "uvicorn.workers.UvicornWorker"

workers = 2

loglevel = "info"
accesslog = "-"
errorlog = "-"
