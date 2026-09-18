import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import RootLayout from '@/app/layout'

describe('Root Layout', () => {
  it('renders children correctly', () => {
    const { container } = render(
      <RootLayout>
        <div>Test Child</div>
      </RootLayout>
    )
    expect(screen.getByText('Test Child')).toBeInTheDocument()
  })

  it('renders html and body tags', () => {
    const { container } = render(
      <RootLayout>
        <div>Test</div>
      </RootLayout>
    )
    expect(container.querySelector('html')).toBeInTheDocument()
    expect(container.querySelector('body')).toBeInTheDocument()
  })

  it('has correct lang attribute', () => {
    const { container } = render(
      <RootLayout>
        <div>Test</div>
      </RootLayout>
    )
    const html = container.querySelector('html')
    expect(html).toHaveAttribute('lang', 'en')
  })
})
