import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <nav className="container mx-auto px-6 py-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-indigo-600">Azolute AI</h1>
          <div className="space-x-4">
            <Link
              href="/login"
              className="text-gray-700 hover:text-indigo-600 transition"
            >
              Login
            </Link>
            <Link
              href="/signup"
              className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            AI-Powered Chatbot
            <br />
            <span className="text-indigo-600">For Your Website</span>
          </h2>
          <p className="text-xl text-gray-600 mb-12">
            Create intelligent chatbots that understand your content, capture
            leads, and provide 24/7 customer support with RAG-powered responses.
          </p>
          <Link
            href="/signup"
            className="bg-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-indigo-700 transition inline-block"
          >
            Start Free Trial
          </Link>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="bg-white p-8 rounded-xl shadow-sm">
            <div className="text-indigo-600 text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold mb-2">Smart Conversations</h3>
            <p className="text-gray-600">
              RAG-powered responses using your knowledge base for accurate answers
            </p>
          </div>
          <div className="bg-white p-8 rounded-xl shadow-sm">
            <div className="text-indigo-600 text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold mb-2">Lead Generation</h3>
            <p className="text-gray-600">
              Capture and manage leads automatically with built-in forms
            </p>
          </div>
          <div className="bg-white p-8 rounded-xl shadow-sm">
            <div className="text-indigo-600 text-4xl mb-4">🎨</div>
            <h3 className="text-xl font-bold mb-2">Fully Customizable</h3>
            <p className="text-gray-600">
              Match your brand with custom colors, logos, and personalities
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
