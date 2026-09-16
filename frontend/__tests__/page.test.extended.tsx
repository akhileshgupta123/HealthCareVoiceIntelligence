import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import Home from '@/app/page'

describe('Home Page Extended', () => {
  it('renders all quick action buttons', () => {
    render(<Home />)
    expect(screen.getByText('Check Claim Status')).toBeInTheDocument()
    expect(screen.getByText('Verify Eligibility')).toBeInTheDocument()
    expect(screen.getByText('Create Ticket')).toBeInTheDocument()
  })

  it('renders all capability items', () => {
    render(<Home />)
    expect(screen.getByText('Claim status inquiries')).toBeInTheDocument()
    expect(screen.getByText('Payment check verification')).toBeInTheDocument()
    expect(screen.getByText('Insurance eligibility checks')).toBeInTheDocument()
    expect(screen.getByText('Policy and procedure queries')).toBeInTheDocument()
    expect(screen.getByText('Escalation ticket creation')).toBeInTheDocument()
  })

  it('renders system status indicators', () => {
    render(<Home />)
    expect(screen.getByText('Voice Connection')).toBeInTheDocument()
    expect(screen.getByText('Moss Retrieval')).toBeInTheDocument()
    expect(screen.getByText('AI Agents')).toBeInTheDocument()
  })

  it('shows disconnected status initially', () => {
    render(<Home />)
    // Check that Voice Connection shows as disconnected in the status card
    const disconnectedElements = screen.getAllByText('Disconnected')
    expect(disconnectedElements.length).toBeGreaterThan(0)
  })

  it('renders correct number of capabilities', () => {
    render(<Home />)
    const checkmarks = screen.getAllByText('✓')
    expect(checkmarks).toHaveLength(5)
  })
})
