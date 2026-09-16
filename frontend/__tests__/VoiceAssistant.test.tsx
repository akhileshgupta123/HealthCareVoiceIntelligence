import { render, screen, fireEvent } from '@testing-library/react'
import VoiceAssistant from '@/components/VoiceAssistant'

describe('VoiceAssistant Component', () => {
  const mockOnConnectionChange = jest.fn()

  beforeEach(() => {
    mockOnConnectionChange.mockClear()
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
})
