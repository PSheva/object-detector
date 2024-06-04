import React, { useRef } from 'react';
import '/src/css/VideoBox.css';

const VideoBox = ({ video, setSidebarContent, deleteVideo }) => {
  const videoRef = useRef(null);

  const playVideo = () => {
    videoRef.current.play();
  };

  const pauseVideo = () => {
    videoRef.current.pause();
  };

  const stopVideo = () => {
    videoRef.current.pause();
    videoRef.current.currentTime = 0;
  };

  return (
    <div className='video-box'>
      <video ref={videoRef} controls>
        <source src={video.url} type='video/mp4' />
        Your browser does not support the video tag.
      </video>
      <div className='video-controls'>
        <button onClick={playVideo}>Play</button>
        <button onClick={pauseVideo}>Pause</button>
        <button onClick={stopVideo}>Stop</button>
        <button onClick={deleteVideo}>Delete</button>
        <button onClick={() => setSidebarContent(video.json)}>Show JSON</button>
      </div>
      {video.tags && video.tags.length > 0 && (
        <div className='tags'>
          <strong>Tags:</strong> {video.tags.join(', ')}
        </div>
      )}
      
    </div>
  );
};

export default VideoBox;
