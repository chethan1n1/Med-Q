import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Download, ArrowLeft, CheckCircle, Send } from 'lucide-react';
import { MedicalSummary, IntakeData } from '../types';
import { intakeService } from '../services/api';

const SummaryPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [intakeData, setIntakeData] = useState<IntakeData | null>(null);
  const [summary, setSummary] = useState<MedicalSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  useEffect(() => {
    if (location.state?.intakeData) {
      setIntakeData(location.state.intakeData);
      generateSummary(location.state.intakeData);
    } else {
      navigate('/');
    }
  }, [location, navigate]);

  const generateSummary = async (data: IntakeData) => {
    setIsLoading(true);
    try {
      const response = await intakeService.generateSummary(data);
      if (response.success && response.data) {
        setSummary(response.data);
      }
    } catch (error) {
      console.error('Error generating summary:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!intakeData) return;
    
    setIsLoading(true);
    try {
      const response = await intakeService.submitPatient(intakeData);
      if (response.success) {
        setIsSubmitted(true);
      }
    } catch (error) {
      console.error('Error submitting patient data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    // TODO: Implement PDF download
    console.log('Download PDF functionality to be implemented');
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-lg mx-4">
          <CardContent className="p-8 text-center">
            <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Successfully Submitted!
            </h2>
            <p className="text-gray-600 mb-6">
              Your medical information has been submitted and will be available to your healthcare provider.
            </p>
            <div className="space-y-3">
              <Button onClick={() => navigate('/')} className="w-full">
                Start New Intake
              </Button>
              <Button 
                variant="outline" 
                onClick={() => navigate('/dashboard')}
                className="w-full"
              >
                Go to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => navigate(-1)}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <h1 className="text-xl font-semibold text-gray-900">Medical Summary</h1>
          </div>
          <Button
            onClick={handleDownloadPDF}
            variant="outline"
            size="sm"
          >
            <Download className="h-4 w-4 mr-2" />
            Download PDF
          </Button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Patient Information */}
        {intakeData && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Patient Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Name</label>
                  <p className="font-semibold">{intakeData.name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Age</label>
                  <p className="font-semibold">{intakeData.age} years</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Gender</label>
                  <p className="font-semibold capitalize">{intakeData.gender}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Symptom Duration</label>
                  <p className="font-semibold">{intakeData.duration}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* AI-Generated Summary */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>AI-Generated Medical Summary</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Generating summary...</span>
              </div>
            ) : summary ? (
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">Summary</h4>
                  <p className="text-gray-700 leading-relaxed">{summary.summary_text}</p>
                </div>

                {summary.structured_data && (
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">Chief Complaint</h4>
                      <p className="text-gray-700">{summary.structured_data.chief_complaint}</p>
                    </div>

                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">Severity</h4>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        summary.structured_data.severity === 'severe' 
                          ? 'bg-red-100 text-red-800'
                          : summary.structured_data.severity === 'moderate'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {summary.structured_data.severity}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">Symptoms</h4>
                      <ul className="list-disc list-inside text-gray-700">
                        {summary.structured_data.symptoms.map((symptom, index) => (
                          <li key={index}>{symptom}</li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">Current Medications</h4>
                      {summary.structured_data.current_medications.length > 0 ? (
                        <ul className="list-disc list-inside text-gray-700">
                          {summary.structured_data.current_medications.map((med, index) => (
                            <li key={index}>{med}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500">None reported</p>
                      )}
                    </div>

                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">Allergies</h4>
                      {summary.structured_data.allergies.length > 0 ? (
                        <ul className="list-disc list-inside text-gray-700">
                          {summary.structured_data.allergies.map((allergy, index) => (
                            <li key={index}>{allergy}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500">None reported</p>
                      )}
                    </div>

                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">Recommendations</h4>
                      <ul className="list-disc list-inside text-gray-700">
                        {summary.structured_data.recommendations.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {summary.icd_codes && summary.icd_codes.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Suggested ICD Codes</h4>
                    <div className="flex flex-wrap gap-2">
                      {summary.icd_codes.map((code, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded">
                          {code}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                Unable to generate summary. Please try again.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Raw Data */}
        {intakeData && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Detailed Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Symptoms Description</label>
                  <p className="text-gray-700 mt-1">{intakeData.symptoms}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Current Medications</label>
                  <p className="text-gray-700 mt-1">{intakeData.medications || 'None'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Allergies</label>
                  <p className="text-gray-700 mt-1">{intakeData.allergies || 'None'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Submit Button */}
        <div className="flex justify-center space-x-4">
          <Button
            onClick={() => navigate(-1)}
            variant="outline"
            size="lg"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go Back
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isLoading}
            size="lg"
            className="min-w-[160px]"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : (
              <Send className="h-4 w-4 mr-2" />
            )}
            Confirm & Submit
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SummaryPage;
