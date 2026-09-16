import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import VoiceAssistant from '@/components/VoiceAssistant'

// Mock fetch globally
global.fetch = jest.fn()

describe('VoiceAssistant Component', () => {
  const mockOnConnectionChange = jest.fn()

  beforeEach(() => {
    mockOnConnectionChange.mockClear()
    ;(global.fetch as jest.Mock).mockClear()
  })

  it('renders voice assistant heading', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const heading = screen.getByText('Voice Assistant')
    expect(heading).toBeInTheDocument()
  })

  it('shows disconnected status initially', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const status = screen.getByText('Disconnected')
    expect(status).toBeInTheDocument()
  })

  it('renders connect button when disconnected', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const connectButton = screen.getByText('Connect Voice')
    expect(connectButton).toBeInTheDocument()
  })

  it('renders conversation instructions', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const instructions = screen.getByText('Try saying:')
    expect(instructions).toBeInTheDocument()
  })

  it('renders example phrases', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    expect(screen.getByText(/Check the status of claim CLM001/)).toBeInTheDocument()
    expect(screen.getByText(/What's the status of check CHK001\?/)).toBeInTheDocument()
  })

  it('fetches token from backend on connect', async () => {
    const mockToken = 'test-jwt-token'
    const mockUrl = 'wss://test.livekit.cloud'
    
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ token: mockToken, url: mockUrl })
    })

    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const connectButton = screen.getByText('Connect Voice')
    fireEvent.click(connectButton)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/livekit/token',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
      )
    })
  })

  it('shows error alert when backend fails', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Backend error' })
    })

    // Mock alert
    window.alert = jest.fn()

    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const connectButton = screen.getByText('Connect Voice')
    fireEvent.click(connectButton)

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith(
        'Failed to connect to voice server. Please ensure the backend is running.'
      )
    })
  })

  it('renders transcript display area', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    expect(screen.getByText('Conversation')).toBeInTheDocument()
  })

  it('renders example phrases in instructions', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    expect(screen.getByText('Try saying:')).toBeInTheDocument()
    expect(screen.getByText(/Check the status of claim CLM001/)).toBeInTheDocument()
  })

  it('renders all example phrases', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    expect(screen.getByText(/What's the status of check CHK001\?/)).toBeInTheDocument()
    expect(screen.getByText(/Check eligibility for patient PAT001/)).toBeInTheDocument()
    expect(screen.getByText(/Create a ticket for billing issue/)).toBeInTheDocument()
    expect(screen.getByText(/What's the policy for claim submission\?/)).toBeInTheDocument()
  })
})
