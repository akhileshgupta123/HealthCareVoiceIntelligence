'use client'

import { useState, useRef, useEffect } from 'react'
import { Room, RoomEvent } from 'livekit-client'

interface SpeechResultEvent extends Event {
  results: {
    length: number
    [index: number]: {
      [index: number]: { transcript: string }
    }
  }
}

interface BrowserSpeechRecognition {
  lang: string
  continuous: boolean
  interimResults: boolean
  start: () => void
  stop: () => void
  onresult: ((event: SpeechResultEvent) => void) | null
  onerror: ((event: Event & { error: string }) => void) | null
  onend: (() => void) | null
}

type SpeechRecognitionConstructor = new () => BrowserSpeechRecognition

interface VoiceAssistantProps {
  onConnectionChange: (connected: boolean) => void
}

export default function VoiceAssistant({ onConnectionChange }: VoiceAssistantProps) {
  const [isConnected, setIsConnected] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [transcript, setTranscript] = useState<string[]>([])
  const [isListening, setIsListening] = useState(false)
  const roomRef = useRef<Room | null>(null)
  const recognitionRef = useRef<BrowserSpeechRecognition | null>(null)
  const audioContainerRef = useRef<HTMLDivElement | null>(null)
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

  const addTranscript = (speaker: 'User' | 'Assistant', text: string) => {
    setTranscript(previous => [...previous, `${speaker}: ${text}`])
  }

  const speak = (text: string) => {
    addTranscript('Assistant', text)
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 1
      window.speechSynthesis.speak(utterance)
    }
  }

  const requestApi = async <T,>(path: string, options?: RequestInit): Promise<T> => {
    const response = await fetch(`${apiBaseUrl}/api/v1${path}`, options)
    const payload = await response.json().catch(() => null)
    if (!response.ok) {
      throw new Error(payload?.detail ?? `Request failed with status ${response.status}`)
    }
    return payload as T
  }

  const processVoiceCommand = async (command: string) => {
    const normalized = command.toLowerCase()
    const claimId = command.toUpperCase().match(/CLM\d+/)?.[0]
    const checkId = command.toUpperCase().match(/CHK\d+/)?.[0]
    const patientId = command.toUpperCase().match(/PAT\d+/)?.[0]

    try {
      if (normalized.includes('claim') && normalized.includes('status')) {
        if (!claimId) {
          speak('Please provide a claim ID, for example C L M zero zero one.')
          return
        }
        const claim = await requestApi<{ id: string; patient_name: string; status: string; amount: number }>(`/claims/${claimId}`)
        speak(`Claim ${claim.id} for ${claim.patient_name} is ${claim.status.replaceAll('_', ' ')}. The amount is ${claim.amount} dollars.`)
        return
      }

      if (normalized.includes('check') && normalized.includes('status')) {
        if (!checkId) {
          speak('Please provide a check ID, for example C H K zero zero one.')
          return
        }
        const check = await requestApi<{ id: string; patient_name: string; status: string; amount: number }>(`/checks/${checkId}`)
        speak(`Check ${check.id} for ${check.patient_name} is ${check.status}. The amount is ${check.amount} dollars.`)
        return
      }

      if (normalized.includes('eligibility')) {
        if (!patientId) {
          speak('Please provide a patient ID, for example P A T zero zero one.')
          return
        }
        const eligibility = await requestApi<{ patient_name: string; status: string; insurance_provider: string }>(`/eligibility/${patientId}`)
        speak(`${eligibility.patient_name} is ${eligibility.status} with ${eligibility.insurance_provider}.`)
        return
      }

      if (normalized.includes('ticket') || normalized.includes('billing issue') || normalized.includes('escalate')) {
        const ticket = await requestApi<{ id: string; priority: string }>(
          '/tickets',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              patient_id: patientId ?? null,
              subject: command,
              description: command,
              priority: normalized.includes('urgent') || normalized.includes('critical') ? 'high' : 'medium',
              category: 'voice-request',
              created_by: 'voice-assistant',
            }),
          },
        )
        speak(`Created ticket ${ticket.id} with ${ticket.priority} priority.`)
        return
      }

      const knowledge = await requestApi<{ results: Array<{ text: string }> }>('/knowledge/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: command, top_k: 1 }),
      })
      speak(knowledge.results[0]?.text ?? 'I could not find a matching policy. Please try a more specific question.')
    } catch (error) {
      console.error('Voice command failed:', error)
      speak(error instanceof Error ? `I could not complete that request. ${error.message}` : 'I could not complete that request.')
    }
  }

  const startListening = () => {
    const browserWindow = window as typeof window & {
      SpeechRecognition?: SpeechRecognitionConstructor
      webkitSpeechRecognition?: SpeechRecognitionConstructor
    }
    const Recognition = browserWindow.SpeechRecognition ?? browserWindow.webkitSpeechRecognition
    if (!Recognition) {
      speak('Speech recognition is not available in this browser. Please use Chrome or Edge.')
      return
    }

    const recognition = new Recognition()
    recognition.lang = 'en-US'
    recognition.continuous = false
    recognition.interimResults = false
    recognition.onresult = event => {
      const spokenText = event.results[event.results.length - 1][0].transcript.trim()
      addTranscript('User', spokenText)
      void processVoiceCommand(spokenText)
    }
    recognition.onerror = event => {
      console.error('Speech recognition failed:', event.error)
      if (event.error !== 'aborted') {
        speak(`I could not hear that request. ${event.error}.`)
      }
    }
    recognition.onend = () => setIsListening(false)
    recognitionRef.current = recognition
    setIsListening(true)
    recognition.start()
  }

  const connectToRoom = async () => {
    try {
      // Fetch token from backend
      const response = await fetch(`${apiBaseUrl}/api/v1/livekit/token`, {
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
        const error = await response.json().catch(() => null)
        console.error('Failed to get LiveKit token:', error)
        alert(error?.detail ?? 'Failed to get a LiveKit token. Please check the backend configuration.')
        return
      }

      const { token, url } = await response.json()

      const room = new Room()
      roomRef.current = room

      await room.connect(url, token)
      room.on(RoomEvent.Disconnected, () => {
        roomRef.current = null
        setIsConnected(false)
        onConnectionChange(false)
      })
      setIsConnected(true)
      onConnectionChange(true)
      await room.localParticipant.setMicrophoneEnabled(true)

      // Handle incoming tracks
      room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        if (track.kind === 'audio') {
          const audioElement = document.createElement('audio')
          audioElement.autoplay = true
          track.attach(audioElement)
          audioContainerRef.current?.appendChild(audioElement)
        }
      })

      console.log('Connected to LiveKit room')
    } catch (error) {
      console.error('Failed to connect to LiveKit:', error)
      roomRef.current?.disconnect()
      roomRef.current = null
      setIsConnected(false)
      onConnectionChange(false)
      alert(error instanceof Error ? `Failed to connect to LiveKit: ${error.message}` : 'Failed to connect to LiveKit.')
    }
  }

  const disconnectFromRoom = async () => {
    recognitionRef.current?.stop()
    window.speechSynthesis?.cancel()
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
    if (isListening) {
      recognitionRef.current?.stop()
      return
    }
    startListening()
  }

  useEffect(() => {
    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect()
      }
      recognitionRef.current?.stop()
      window.speechSynthesis?.cancel()
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

        {isConnected && (
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

      <div ref={audioContainerRef} className="hidden" />

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
