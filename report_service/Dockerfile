FROM python:3.8

# RUN mkdir -p ~/.config/pip && \
#     echo \
#     "[global]\n" \
#     "no-cache-dir = true\n" \
#     "trusted-host = 172.21.100.15\n" \
#     "index = http://172.21.100.15:8081/repository/pypi-all/pypi\n" \
#     "index-url = http://172.21.100.15:8081/repository/pypi-all/simple" \
#     > ~/.config/pip/pip.conf

# avoid-extension-reinstalls
RUN mkdir -p /root/.vscode-server/extensions

# install requirements.txt and onvif_zeep for service
WORKDIR /usr/src/app/report_manager
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt && rm requirements.txt

# copy source folder and set pythonpath environment
COPY report_manager .
ENV TZ Asia/Ho_Chi_Minh

CMD [ "bash", "-c", "python main.py" ]