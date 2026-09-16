'use client'

import { useState, useRef, useEffect } from 'react'
import { Room, RoomEvent, Track } from 'livekit-client'

interface VoiceAssistantProps {
  onConnectionChange: (connected: boolean) => void
}

export default function VoiceAssistant({ onConnectionChange }: VoiceAssistantProps) {
  const [isConnected, setIsConnected] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [transcript, setTranscript] = useState<string[]>([])
  const [isListening, setIsListening] = useState(false)
  const roomRef = useRef<Room | null>(null)

  const connectToRoom = async () => {
    try {
      // Fetch token from backend
      const response = await fetch('http://localhost:8000/api/v1/livekit/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          room_name: 'healthcare-ops-room',
          participant_name: 'user-' + Math.random().toString(36).substr(2, 9)
        })
      })

      if (!response.ok) {
        const error = await response.json()
        console.error('Failed to get LiveKit token:', error)
        alert('Failed to connect to voice server. Please ensure the backend is running.')
        return
      }

      const { token, url } = await response.json()

      const room = new Room()
      roomRef.current = room

      await room.connect(url, token)
      setIsConnected(true)
      onConnectionChange(true)

      // Handle incoming tracks
      room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        if (track.kind === 'audio') {
          const audioElement = document.createElement('audio')
          audioElement.autoplay = true
          track.attach(audioElement)
        }
      })

      // Handle transcription events
      // Note: TranscriptionReceived may not be available in current livekit-client version
      // room.on(RoomEvent.TranscriptionReceived, (segments) => {
      //   const text = segments.map(s => s.text).join(' ')
      //   setTranscript(prev => [...prev, `User: ${text}`])
      // })

      console.log('Connected to LiveKit room')
    } catch (error) {
      console.error('Failed to connect to LiveKit:', error)
      alert('Failed to connect to voice server. Please check your configuration.')
    }
  }

  const disconnectFromRoom = async () => {
    if (roomRef.current) {
      await roomRef.current.disconnect()
      roomRef.current = null
      setIsConnected(false)
      onConnectionChange(false)
    }
  }

  const toggleMute = () => {
    if (roomRef.current) {
      roomRef.current.localParticipant.setMicrophoneEnabled(!isMuted)
      setIsMuted(!isMuted)
    }
  }

  const toggleListening = () => {
    setIsListening(!isListening)
    // In a real implementation, this would control VAD settings
  }

  useEffect(() => {
    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect()
      }
    }
  }, [])

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Voice Assistant</h2>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Live' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Connection Controls */}
      <div className="flex space-x-4 mb-6">
        {!isConnected ? (
          <button
            onClick={connectToRoom}
            className="flex-1 bg-primary-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            Connect Voice
          </button>
        ) : (
          <button
            onClick={disconnectFromRoom}
            className="flex-1 bg-red-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-red-700 transition-colors"
          >
            Disconnect
          </button>
        )}

        {isConnected && (
          <>
            <button
              onClick={toggleMute}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                isMuted
                  ? 'bg-gray-200 text-gray-800'
                  : 'bg-primary-100 text-primary-800'
              }`}
            >
              {isMuted ? 'Unmute' : 'Mute'}
            </button>

            <button
              onClick={toggleListening}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                isListening
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {isListening ? 'Listening' : 'Tap to Speak'}
            </button>
          </>
        )}
      </div>

      {/* Transcript Display */}
      <div className="bg-gray-50 rounded-lg p-4 h-64 overflow-y-auto mb-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">Conversation</h3>
        {transcript.length === 0 ? (
          <p className="text-gray-400 text-sm">
            {isConnected
              ? 'Start speaking to interact with the assistant...'
              : 'Connect to voice to begin conversation...'}
          </p>
        ) : (
          <div className="space-y-2">
            {transcript.map((line, index) => (
              <div
                key={index}
                className={`text-sm ${
                  line.startsWith('User:')
                    ? 'text-blue-700'
                    : 'text-green-700'
                }`}
              >
                {line}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="text-sm text-gray-600">
        <p className="font-medium mb-1">Try saying:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>"Check the status of claim CLM001"</li>
          <li>"What's the status of check CHK001?"</li>
          <li>"Check eligibility for patient PAT001"</li>
          <li>"Create a ticket for billing issue"</li>
          <li>"What's the policy for claim submission?"</li>
        </ul>
      </div>
    </div>
  )
}
