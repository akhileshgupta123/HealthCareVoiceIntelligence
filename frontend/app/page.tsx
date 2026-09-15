'use client'

import { useState } from 'react'
import VoiceAssistant from '@/components/VoiceAssistant'

export default function Home() {
  const [isConnected, setIsConnected] = useState(false)

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Healthcare Operations Assistant
          </h1>
          <p className="text-gray-600">
            Real-Time Voice AI for Claims, Payments, and Support
          </p>
        </header>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Voice Assistant */}
          <div className="lg:col-span-2">
            <VoiceAssistant onConnectionChange={setIsConnected} />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Status Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">System Status</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Voice Connection</span>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    isConnected ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Moss Retrieval</span>
                  <span className="px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
                    Active
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">AI Agents</span>
                  <span className="px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
                    Ready
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
              <div className="space-y-2">
                <button className="w-full text-left px-4 py-3 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors">
                  <span className="font-medium">Check Claim Status</span>
                  <p className="text-sm text-gray-600">"Check claim CLM001 status"</p>
                </button>
                <button className="w-full text-left px-4 py-3 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors">
                  <span className="font-medium">Verify Eligibility</span>
                  <p className="text-sm text-gray-600">"Check eligibility for PAT001"</p>
                </button>
                <button className="w-full text-left px-4 py-3 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors">
                  <span className="font-medium">Create Ticket</span>
                  <p className="text-sm text-gray-600">"Create a ticket for billing issue"</p>
                </button>
              </div>
            </div>

            {/* Capabilities */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Capabilities</h2>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>Claim status inquiries</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>Payment check verification</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>Insurance eligibility checks</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>Policy and procedure queries</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>Escalation ticket creation</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
