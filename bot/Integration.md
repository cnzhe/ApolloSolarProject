# Steps to Integrate the Chatbot Widget

## Copy the Build to Main App
Mac/Linux
```
cp -r ./bot/frontend/dist/* ./main-app/public/chat-widget/
```

**Replace `main-app` with web app directory name**

## Add Widget to Frontend
In the main app's component (e.g. `MainApp.jsx`), load the widget's JavaScript.
```
import React, { useEffect } from 'react';

const MainApp = () => {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = '/bot/frontend/assets/index-16e9a009.js'; 
    script.async = true;  // Ensure it loads asynchronously
    document.body.appendChild(script);
    
    return () => {
      document.body.removeChild(script);  // Cleanup the script when component is unmounted
    };
  }, []);

  return (
    <div>
      <h1>Main App</h1>
      {/* The rest of your main app content */}
    </div>
  );
};

export default MainApp;
```