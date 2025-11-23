import React, { useEffect, useRef } from 'react';

interface HtmlPreviewProps {
  htmlContent: string;
}

const HtmlPreview: React.FC<HtmlPreviewProps> = ({ htmlContent }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (iframeRef.current && iframeRef.current.contentDocument) {
      iframeRef.current.contentDocument.open();
      iframeRef.current.contentDocument.write(htmlContent);
      iframeRef.current.contentDocument.close();
    }
  }, [htmlContent]);

  return (
    <div className="border border-gray-200 rounded-md overflow-hidden">
      <iframe
        ref={iframeRef}
        title="Email Preview"
        className="w-full h-96"
        sandbox="allow-same-origin"
      />
    </div>
  );
};

export default HtmlPreview;