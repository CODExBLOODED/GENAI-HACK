import React, { useEffect } from "react";
import axios from "axios";
import './App.css';
import Webcam from "react-webcam";
import * as cocoSsd from "@tensorflow-models/coco-ssd";
import Speech from "react-speech";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';


function App() {
  const constraints = { video: true };
  const webcamRef = React.useRef(null);
  const [objectLabel, setObjectLabel] = React.useState("");
  const [message, setMessage] = React.useState("");
  const { transcript, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/data')
      .then(response => {
        console.log(response.data);
        console.log("Connected to the server and connected with the flask application")
        // Here you can set your state variables with the data received
      })
      .catch(error => {
        console.error('Error fetching data', error);
      });
  }, []);  // Empty array means this effect runs once on mount


  const handleInputChange = (event) => {
    setMessage(event.target.value || transcript);
  };

  const handleSpeechConversion = () => {
    const speech = new SpeechSynthesisUtterance();
    speech.text = message;
    window.speechSynthesis.speak(speech);
  };

  const handleSpeechRecognition = () => {
    SpeechRecognition.startListening();
  };

  React.useEffect(() => {
    const runObjectDetection = async () => {
      const net = await cocoSsd.load();
      setInterval(() => {
        detect(net);
      }, 1000);
    };

    const detect = async (net) => {
      if (webcamRef.current && webcamRef.current.video.readyState === 4) {
        const video = webcamRef.current.video;
        const { videoWidth, videoHeight } = video;
        webcamRef.current.video.width = videoWidth;
        webcamRef.current.video.height = videoHeight;

        const predictions = await net.detect(video);
        if (predictions.length > 0) {
          const object = predictions[0].class;
          setObjectLabel(object);
          speak(object);
        } else {
          setObjectLabel("");
        }
      }
    };

    const speak = (text) => {
      const speech = new SpeechSynthesisUtterance();
      speech.text = text;
      speechSynthesis.speak(speech);
    };

    navigator.mediaDevices.getUserMedia(constraints)
      .then(function(mediaStream) {
        const video = document.getElementById('videoElement');
        video.srcObject = mediaStream;
        video.onloadedmetadata = function(e) {
          video.play();
          runObjectDetection();
        };
      })
      .catch(function(err) {
        console.error('Error accessing the webcam: ', err);
      });
  }, []);

  if (!browserSupportsSpeechRecognition) {
    return <span>Browser doesn't support speech recognition.</span>;
  }

  return (
    <div className="App">
      <Webcam ref={webcamRef} />
      <p>Object: {objectLabel}</p>
      <input type="text" value={message} onChange={handleInputChange} />
      <button onClick={handleSpeechConversion}>Convert to Speech</button>
      <button onClick={SpeechRecognition.startListening}>Start</button>
      <button onClick={SpeechRecognition.stopListening}>Stop</button>
      <button onClick={resetTranscript}>Reset</button>
      <p>{transcript}</p>
      <Speech text={message} />
    </div>
  );
}

export default App;