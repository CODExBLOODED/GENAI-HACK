import React from "react";
import './App.css';
import Webcam from "react-webcam";
import * as cocoSsd from "@tensorflow-models/coco-ssd";
import Speech from "react-speech"

function App() {
  const constraints = { video: true };
  const webcamRef = React.useRef(null);
  const [objectLabel, setObjectLabel] = React.useState("");
  const [message, setMessage] = React.useState("");

  const handleInputChange = (event) => {
    setMessage(event.target.value);
  };

  const handleSpeechConversion = () => {
    const speech = new SpeechSynthesisUtterance();
    speech.text = message;
    window.speechSynthesis.speak(speech);
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

  return (
    <div className="App">
      <Webcam ref={webcamRef} />
      <p>Object: {objectLabel}</p>
      <input type="text" value={message} onChange={handleInputChange} />
      <button onClick={handleSpeechConversion}>Convert to Speech</button>
      <Speech text={message} />
    </div>
  );
}

export default App;
