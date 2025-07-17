import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent } from '../components/ui/card';
import { Mic, MicOff, Send, ArrowLeft, User, Bot } from 'lucide-react';
import { ChatMessage, IntakeData, IntakeStep } from '../types';
import { intakeService } from '../services/api';
import { generateId } from '../utils';

const ChatIntakePage: React.FC = () => {
  const { mode } = useParams<{ mode: 'voice' | 'text' }>();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [showSummaryOptions, setShowSummaryOptions] = useState(false);
  const [summaryText, setSummaryText] = useState<string>('');
  const [intakeData, setIntakeData] = useState<IntakeData>({
    name: '',
    age: undefined,
    gender: '',
    symptoms: '',
    duration: '',
    medications: '',
    allergies: '',
    current_step: 'name'
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  const stepQuestions = {
    name: "Hello! I'm Dr. Sarah, your AI medical assistant. I'm here to help gather information before your consultation using intelligent, compassionate guidance. This will help your healthcare provider better understand your concerns and provide more focused care. May I start by getting your name?",
    age: "Thank you for sharing your name! To help me understand your medical profile better, could you tell me your age?",
    gender: "Perfect! Now, what's your gender? You can say male, female, or other.",
    symptoms: "Now I'd like to understand what brought you here today. Could you describe your main symptoms or health concerns? Please take your time and share as much detail as you're comfortable with.",
    duration: "I understand you're experiencing these symptoms. That must be concerning for you. To help your healthcare provider understand the timeline, how long have you been experiencing these symptoms?",
    medications: "Thank you for that information. Now, are you currently taking any medications? This includes prescription medications, over-the-counter drugs, vitamins, or supplements. If you're not taking anything, just say 'none'.",
    allergies: "I've noted your medication information. Lastly, do you have any allergies I should know about? This includes food allergies, drug allergies, or environmental allergies. If you don't have any, just say 'none'.",
    summary: "Perfect! Thank you for providing all that information. I now have everything I need to create a comprehensive summary for your healthcare provider. This will help them understand your situation quickly and focus on addressing your concerns."
  };

  useEffect(() => {
    // Start with welcome message
    const welcomeMessage: ChatMessage = {
      id: generateId(),
      type: 'bot',
      content: stepQuestions.name,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startRecording = async () => {
    try {
      // Check if browser supports speech recognition
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      
      if (!SpeechRecognition) {
        alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
        return;
      }

      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsRecording(true);
        console.log('Speech recognition started');
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        console.log('Speech recognition result:', transcript);
        processTextInput(transcript);
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        
        let errorMessage = 'Speech recognition failed. ';
        switch(event.error) {
          case 'no-speech':
            errorMessage += 'No speech was detected. Please try again.';
            break;
          case 'audio-capture':
            errorMessage += 'No microphone was found. Please check your microphone.';
            break;
          case 'not-allowed':
            errorMessage += 'Microphone access was denied. Please allow microphone access.';
            break;
          default:
            errorMessage += 'Please try again.';
        }
        
        const errorChatMessage: ChatMessage = {
          id: generateId(),
          type: 'bot',
          content: errorMessage,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorChatMessage]);
      };

      recognition.onend = () => {
        setIsRecording(false);
        recognitionRef.current = null;
        console.log('Speech recognition ended');
      };

      recognition.start();
      
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
  };

  const processTextInput = async (text: string) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: generateId(),
      type: 'user',
      content: text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);
    try {
      // Process with enhanced intelligent intake
      const response = await intakeService.processText(text, intakeData);
      
      if (response.success && response.data) {
        // Add bot response message
        const botMessage: ChatMessage = {
          id: generateId(),
          type: 'bot',
          content: response.data.response,
          timestamp: new Date(),
          isEmergency: response.data.is_emergency
        };
        setMessages(prev => [...prev, botMessage]);
        
        // Always update intake data with extracted data and next step
        setIntakeData(prev => {
          const updated = {
            ...prev,
            ...response.data!.extracted_data,
            current_step: response.data!.next_step as IntakeStep
          };
          console.log('Updated intake data:', updated);
          return updated;
        });
        
        // If we've reached summary step, show completion options
        if (response.data.next_step === 'summary') {
          setShowSummaryOptions(true);
        }
      }
    } catch (error) {
      console.error('Error processing text:', error);
      const errorMessage: ChatMessage = {
        id: generateId(),
        type: 'bot',
        content: "I'm sorry, I'm having trouble processing that. Could you please try again?",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = () => {
    if (currentInput.trim()) {
      processTextInput(currentInput);
      setCurrentInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const generateSummary = async () => {
    if (isGeneratingSummary) return; // Prevent multiple clicks
    
    setIsGeneratingSummary(true);
    try {
      const response = await intakeService.generateSummary(intakeData);
      if (response.success && response.data) {
        setSummaryText(response.data.summary_text);
        
        // Add summary to chat
        const summaryMessage: ChatMessage = {
          id: generateId(),
          type: 'bot',
          content: `Here's your medical summary:\n\n${response.data.summary_text}`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, summaryMessage]);
        setShowSummaryOptions(false); // Hide summary options after generating
      }
    } catch (error) {
      console.error('Error generating summary:', error);
      const errorMessage: ChatMessage = {
        id: generateId(),
        type: 'bot',
        content: "I'm sorry, I couldn't generate the summary right now. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsGeneratingSummary(false);
    }
  };

  const downloadSummary = () => {
    if (!summaryText) return;
    
    const summaryContent = `
MEDICAL INTAKE SUMMARY
Generated: ${new Date().toLocaleString()}

Patient: ${intakeData.name || 'N/A'}
Age: ${intakeData.age || 'N/A'}
Gender: ${intakeData.gender || 'N/A'}

${summaryText}
    `.trim();

    const blob = new Blob([summaryContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `medical-summary-${intakeData.name || 'patient'}-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => navigate('/')}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <h1 className="text-xl font-semibold text-gray-900">Medical Intake</h1>
          </div>
          <div className="text-sm text-gray-500">
            Mode: {mode === 'voice' ? 'Voice + Text' : 'Text Only'}
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="space-y-4 mb-6" style={{ minHeight: 'calc(100vh - 240px)' }}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`flex max-w-[80%] space-x-3 ${
                  message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {message.type === 'user' ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </div>
                <Card
                  className={`${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white border-gray-200'
                  }`}
                >
                  <CardContent className="p-3">
                    <p className="text-sm">{message.content}</p>
                    <div className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-gray-600" />
                </div>
                <Card className="bg-white border-gray-200">
                  <CardContent className="p-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex space-x-3">
            <Input
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1"
            />
            
            {mode === 'voice' && (
              <Button
                onClick={isRecording ? stopRecording : startRecording}
                variant={isRecording ? "destructive" : "outline"}
                size="icon"
                disabled={isLoading}
                title={isRecording ? "Stop voice input" : "Start voice input (uses browser speech recognition)"}
                className={isRecording ? "animate-pulse" : ""}
              >
                {isRecording ? (
                  <MicOff className="h-4 w-4" />
                ) : (
                  <Mic className="h-4 w-4" />
                )}
              </Button>
            )}
            
            <Button
              onClick={handleSendMessage}
              disabled={!currentInput.trim() || isLoading}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          
          {mode === 'voice' && (
            <p className="text-xs text-gray-500 mt-2 text-center">
              {isRecording ? 'Listening... Speak clearly. Recording will stop automatically when you finish.' : 'Click mic to start voice input or type your message'}
            </p>
          )}
        </div>

        {/* Summary Options */}
        {showSummaryOptions && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              Medical Summary Options
            </h3>
            <div className="flex flex-wrap gap-3">
              <Button
                onClick={generateSummary}
                disabled={isGeneratingSummary}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isGeneratingSummary ? 'Generating...' : 'Generate Summary'}
              </Button>
              
              {summaryText && (
                <Button
                  onClick={downloadSummary}
                  variant="outline"
                  className="border-blue-300 text-blue-700 hover:bg-blue-50"
                >
                  Download Summary
                </Button>
              )}
            </div>
            
            {summaryText && (
              <div className="mt-3 p-3 bg-white rounded border">
                <p className="text-sm text-gray-600">
                  Summary generated successfully! You can view it in the chat above or download it as a text file.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatIntakePage;
