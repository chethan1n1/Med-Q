import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Mic, MessageSquare, Shield, Stethoscope, Zap, Users } from 'lucide-react';

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();

  const handleVoiceStart = () => {
    navigate('/intake/voice');
  };

  const handleTextStart = () => {
    navigate('/intake/text');
  };

  const features = [
    {
      icon: <Mic className="h-8 w-8 text-blue-600" />,
      title: "Voice-Powered Intake",
      description: "Speak naturally with our intelligent AI assistant that understands and responds compassionately"
    },
    {
      icon: <MessageSquare className="h-8 w-8 text-green-600" />,
      title: "Intelligent Text Chat",
      description: "Smart conversations that ask follow-up questions and provide personalized guidance"
    },
    {
      icon: <Stethoscope className="h-8 w-8 text-purple-600" />,
      title: "AI Medical Summary",
      description: "Generates comprehensive, structured summaries for healthcare providers"
    },
    {
      icon: <Shield className="h-8 w-8 text-red-600" />,
      title: "Safe & Emergency-Aware",
      description: "Automatically detects emergency symptoms and provides immediate guidance"
    },
    {
      icon: <Zap className="h-8 w-8 text-yellow-600" />,
      title: "Compassionate Intelligence",
      description: "Empathetic responses that make you feel heard and understood"
    },
    {
      icon: <Users className="h-8 w-8 text-indigo-600" />,
      title: "Patient-Centered Care",
      description: "Designed with patient comfort, safety, and dignity in mind"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      {/* Header */}
      <header className="px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Stethoscope className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">MedQ</h1>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Smart Medical Intake
            <span className="block text-blue-600">Powered by AI</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Share your symptoms and medical history through voice or text. 
            Our AI creates a comprehensive summary for your healthcare provider, 
            making your consultation more efficient and focused.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <Button 
              onClick={handleVoiceStart}
              size="lg"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 text-lg min-w-[200px]"
            >
              <Mic className="mr-3 h-5 w-5" />
              Start with Voice
            </Button>
            <Button 
              onClick={handleTextStart}
              variant="outline"
              size="lg"
              className="border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-4 text-lg min-w-[200px]"
            >
              <MessageSquare className="mr-3 h-5 w-5" />
              Start with Text
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="border-gray-200 hover:shadow-lg transition-shadow">
              <CardContent className="p-6 text-center">
                <div className="mb-4 flex justify-center">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* How it Works */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-8">
            How MedQ Works
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">Share Your Story</h4>
              <p className="text-gray-600">
                Use voice or text to describe your symptoms, medical history, and concerns
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-green-600">2</span>
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">AI Analysis</h4>
              <p className="text-gray-600">
                Our AI processes your information and creates a structured medical summary
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-purple-600">3</span>
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">Better Care</h4>
              <p className="text-gray-600">
                Your doctor receives organized information for a more focused consultation
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Stethoscope className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold">MedQ</span>
          </div>
          <p className="text-gray-400 mb-4">
            Transforming healthcare through intelligent patient intake
          </p>
          <p className="text-sm text-gray-500">
            © 2025 MedQ. All rights reserved. | Privacy Policy | Terms of Service
          </p>
        </div>
      </footer>
    </div>
  );
};

export default WelcomePage;
