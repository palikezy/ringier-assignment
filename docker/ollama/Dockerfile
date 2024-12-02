FROM ollama/ollama:latest

ARG LLM_MODEL=llama3.2:1b
ENV LLM_MODEL=$LLM_MODEL

RUN ollama serve & sleep 5 ; \
    ollama pull $LLM_MODEL ; \
    echo "kill 'ollama serve' process" ; \
    ps -ef | grep 'ollama serve' | grep -v grep | awk '{print $2}' | xargs -r kill -9
