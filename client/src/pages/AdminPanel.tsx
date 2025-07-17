import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const AdminPanel: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Card className="m-4">
        <CardHeader>
          <CardTitle>Admin Panel</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Analytics, reports, and administrative functions
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminPanel;
