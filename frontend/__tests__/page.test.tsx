import { render, screen } from '@testing-library/react'
import Home from '@/app/page'

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Home />)
    const heading = screen.getByText('Healthcare Operations Assistant')
    expect(heading).toBeInTheDocument()
  })

  it('renders the subtitle', () => {
    render(<Home />)
    const subtitle = screen.getByText('Real-Time Voice AI for Claims, Payments, and Support')
    expect(subtitle).toBeInTheDocument()
  })

  it('renders system status card', () => {
    render(<Home />)
    const statusHeading = screen.getByText('System Status')
    expect(statusHeading).toBeInTheDocument()
  })

  it('renders quick actions card', () => {
    render(<Home />)
    const actionsHeading = screen.getByText('Quick Actions')
    expect(actionsHeading).toBeInTheDocument()
  })

  it('renders capabilities card', () => {
    render(<Home />)
    const capabilitiesHeading = screen.getByText('Capabilities')
    expect(capabilitiesHeading).toBeInTheDocument()
  })

  it('renders voice assistant component', () => {
    render(<Home />)
    const voiceHeading = screen.getByText('Voice Assistant')
    expect(voiceHeading).toBeInTheDocument()
  })
})
