'use client';
import SimliFaceStream from "@/components/SimliFaceStream/SimliFaceStream";
import Image from "next/image";
import Link from "next/link";
import { useRef, useState } from "react";

export default function Home() {

  const [playing, setPlaying] = useState(false);

  const simliFaceStreamRef = useRef(null);
  const [sessionToken, setSessionToken] = useState("");
  const [minimumChunkSizeState, setMinimumChunkSizeState] = useState(6);
  const [faceId, setFaceId] = useState("04d062bc-00ce-4bb0-ace9-76880e3987ec");

  const StartAudioToVideoSession = async (faceId: string, isJPG: Boolean, syncAudio: Boolean) => {
    const metadata = {
      faceId: faceId,
      isJPG: isJPG,
      apiKey: process.env.NEXT_PUBLIC_SIMLI_API_KEY,
      syncAudio: syncAudio,
    };
  
    const response = await fetch(
      'https://api.simli.ai/startAudioToVideoSession',
      {
        method: 'POST',
        body: JSON.stringify(metadata),
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  
    return response.json();
  };

  const handleStart = async () => {
    try {
      StartAudioToVideoSession(faceId, true, true).then((response) => {
        console.log("Session Token:", response);
        setSessionToken(response.session_token);
        const ws = new WebSocket("ws://localhost:9000/audio");
        ws.onopen = () => {
          console.log("Connected to audio websocket");
        };
  
        ws.onmessage = (event) => {
          // console.log("Received audio data", event.data);
          if (simliFaceStreamRef.current) {
            simliFaceStreamRef.current.sendAudioDataToLipsync(event.data);
          }
        };
      });
      
      
    } catch (error) {
      console.log("Error websocket", error);  
    }
    // StartAudioToVideoSession(faceId, true, true).then((response) => {
    //   console.log("Session Token:", response);
    //   setSessionToken(response.session_token);
    //   setStart(true);
    // });
  }

  const handlePause = () => {
    setPlaying(false);
  };

  const handleResume = () => {
    setPlaying(true);
  };

  const handleMinimumChunkSizeChange = (event: any) => {
    setPlaying(false);
    setMinimumChunkSizeState(parseInt(event.target.value));
  };


  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 font-mono">
        <>
        {
          sessionToken === "" ? ( 
            <div></div>
          ) : (
            <SimliFaceStream ref={simliFaceStreamRef} start={true} sessionToken={sessionToken} minimumChunkSize={minimumChunkSizeState} />
          )
        }
          
          <br />
          <button
            className={
              "hover:opacity-75 text-white font-bold py-2 w-[300px] px-4 rounded" +
              (playing ? " bg-red-500" : " bg-green-500")
            }
            onClick={() => {
              playing ? handlePause() : handleStart();
            }}
          >
            {playing ? "Stop" : "Play"}
          </button>
          <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex"></div>
        </>
      {/* )} */}

    </main>
  );
}
