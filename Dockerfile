FROM python

LABEL version="1.0"
LABEL description="Plotly web page for visualizing Tensorflow Spiking Neural Network models."
LABEL maintainer = "Louis Ross <louis.ross@gmail.com"

WORKDIR /visualizer


RUN ls
RUN ["pip", "install", "dash"]
RUN ["pip", "install", "dash_slicer"]
RUN ["pip", "install", "pandas"]
RUN ["pip", "install", "imageio"]
RUN ["pip", "install", "chart_studio"]
RUN ["pip", "install", "seaborn"]
RUN ["pip", "install", "pyorbital"]

COPY . .

EXPOSE 8050

CMD ["bash"]
