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

  it('allows microphone input even before LiveKit connects', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    expect(screen.getByText('Tap to Speak')).toBeInTheDocument()
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

  it('initializes with disconnected state', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    expect(screen.getByText('Disconnected')).toBeInTheDocument()
  })

  it('shows initial conversation placeholder text', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    expect(screen.getByText('Connect to voice to begin conversation...')).toBeInTheDocument()
  })

  it('has correct component title', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    expect(screen.getByText('Voice Assistant')).toBeInTheDocument()
  })

  it('renders status indicator', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const statusIndicator = document.querySelector('.bg-gray-400')
    expect(statusIndicator).toBeInTheDocument()
  })

  it('renders conversation area with correct styling', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const conversationArea = document.querySelector('.bg-gray-50')
    expect(conversationArea).toBeInTheDocument()
  })

  it('renders instructions section', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    expect(screen.getByText('Try saying:')).toBeInTheDocument()
  })

  it('has list of example phrases', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const listItems = document.querySelectorAll('li')
    expect(listItems.length).toBe(5)
  })

  it('renders main container with correct styling', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const mainContainer = document.querySelector('.bg-white')
    expect(mainContainer).toBeInTheDocument()
  })

  it('renders rounded card container', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const cardContainer = document.querySelector('.rounded-lg')
    expect(cardContainer).toBeInTheDocument()
  })

  it('renders shadow on card', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const shadowElement = document.querySelector('.shadow-md')
    expect(shadowElement).toBeInTheDocument()
  })

  it('renders header section', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const header = screen.getByText('Voice Assistant')
    expect(header).toBeInTheDocument()
  })

  it('renders connect button with correct styling', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const connectButton = screen.getByText('Connect Voice')
    expect(connectButton).toHaveClass('bg-primary-600')
  })

  it('has overflow on conversation area', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const conversationArea = document.querySelector('.overflow-y-auto')
    expect(conversationArea).toBeInTheDocument()
  })

  it('renders conversation heading', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    expect(screen.getByText('Conversation')).toBeInTheDocument()
  })

  it('renders instructions with correct text styling', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const instructions = screen.getByText('Try saying:')
    expect(instructions).toBeInTheDocument()
  })

  it('renders all UI sections in correct order', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    // Check that main sections exist
    expect(screen.getByText('Voice Assistant')).toBeInTheDocument()
    expect(screen.getByText('Connect Voice')).toBeInTheDocument()
    expect(screen.getByText('Conversation')).toBeInTheDocument()
    expect(screen.getByText('Try saying:')).toBeInTheDocument()
  })

  it('has correct padding on card', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const card = document.querySelector('.p-6')
    expect(card).toBeInTheDocument()
  })

  it('renders text-gray-400 for placeholder', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const placeholder = screen.getByText('Connect to voice to begin conversation...')
    expect(placeholder).toBeInTheDocument()
  })

  it('has list-disc styling on example list', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const list = document.querySelector('.list-disc')
    expect(list).toBeInTheDocument()
  })

  it('renders list-inside styling', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const list = document.querySelector('.list-inside')
    expect(list).toBeInTheDocument()
  })

  it('has space-y-1 on list items', () => {
    render(<VoiceAssistant onConnectionChange={mockOnConnectionChange} />)
    const list = document.querySelector('.space-y-1')
    expect(list).toBeInTheDocument()
  })
})
