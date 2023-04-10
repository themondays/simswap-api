# SimSwap Service API

SimSwap Service API is a Python-based flask web service that allows users to swap faces in video and streams using the [SimSwap](https://github.com/neuralchen/SimSwap.git) framework. The service utilizes the Flask web framework to expose a RESTful API that clients can use to send video streams or images and receive the processed output.

## Features

* Real-time face swapping in video streams
* Face swapping in video
* Configurable settings for processing
* Support for Amazon S3 storage
* Extensive error handling
* Thorough documentation and examples

## Installation

### Clone the repository:

```
git clone https://github.com/themondays/simswap-api.git
cd simswap-api
```

### Clone SimSwap project:

```
git clone https://github.com/neuralchen/SimSwap.git SimSwap
```

### Install the required Python packages:

```
pip install -r requirements.txt
```

### Configure the service by editing the config.yaml file. Update the following settings:

* AWS access key and secret access key
* AWS S3 bucket name
* Task directory
* Any other settings as needed

### Run the service:

```
python app.py
```

## Usage

### API Endpoints

The following API endpoints are exposed by the service:

* POST /api/stream/start: Starts the video streaming service with the provided settings.
* POST /api/stream/stop: Stops the video streaming service.
* GET /api/stream: Retrieves the video stream with swapped faces.
* POST /api/swap/create: Swaps faces in a provided video (provides a job ID).
* GET /api/swap/<guid>: Provides job details including URL to final video.

### Examples
Here are some examples of how to use the API endpoints:

#### Start the video streaming service:

```
curl -X POST http://localhost:8000/api/start -H "Content-Type: application/json" -d '{"target": "path/to/tom-henks.jpg"}'
```

#### Stop the video streaming service:

```
curl -X POST http://localhost:8000/api/stream/stop
```

#### View the video stream with swapped faces in your browser:

```
http://localhost:8000/api/stream/stream
```

#### Swap faces in an video:

```
curl -X POST http://localhost:8000/api/swap/create -H "Content-Type: application/json" -d '{"targets": [{"face":"path/to/input_image.jpg"}], "video": "path/to/forest-gump.mp4"}'

# NB: Currently working only with first target
```
## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you find a bug or have a suggestion for improvement.

## License

This project is licensed under the [MIT License](https://github.com/themondays/simswap-api/blob/main/LICENSE). See the LICENSE file for details.

