import React, { useRef, useState, useEffect } from "react";
import { useNavigate} from "react-router-dom";
import { Search } from "lucide-react";
import  file from '/file.svg'

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState("");
  const [filePath, setFilePath] = useState("Your/Path/To/Image")
  const fileInputRef = useRef(null); // Ref for the hidden file input
  const navigator = useNavigate();
  // Handle file selection
  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  useEffect(() => {
    if (selectedFile) {
      setFilePath(selectedFile.name)
    }
  }, [selectedFile])

  // Trigger file input when "Upload" button is clicked
  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage("Please select a file before uploading.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    navigator("/output");
    try {
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        navigator("/");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
  
        // Trigger file download
        const a = document.createElement("a");
        a.href = url;
        a.download = "result.net"; // Ensure this matches the file name
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url); // Clean up the object URL

      } else {
        const errorData = await response.json();
        setMessage(`Error: ${errorData.error}`);
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    }
  };

  return (
    <div className="flex flex-col h-[100vh] bg-[#0a0a0a] text-white justify-center items-center gap-4">
      <h1 className="text-7xl poppins-extrabold tracking-wide">SKETCH 2 PCB</h1>
      <div className="flex flex-row gap-5">
        <div className="flex flex-row-reverse w-96 bg-[#0a0a0a] border-2 border-[#2d2d2d] rounded-lg p-2">
          <button
            className="p-4 border-2 border-[#2d2d2d] rounded-lg bg-[#0a0a0a] hover:bg-[#454545] text-xs hover:border-[#454545] font-hite"
            onClick={triggerFileInput} // Trigger file input on button click
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-folder"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
          </button>
          <input className="w-[100%] bg-[#0a0a0a]" readOnly placeholder={filePath}></input>
        </div>
        <button
          className="px-10 py-3 border-2 border-[#2d2d2d] rounded-lg bg-[#0a0a0a] hover:bg-[#454545] text-xs hover:border-[#454545]"
          onClick={handleUpload} // Call handleUpload on button click
        > 
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-upload"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
        </button>
      </div>
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: "none" }} // Hide the file input element
        onChange={handleFileChange} // Handle file selection
      />
      {message && <p className="mt-4 text-sm">{message}</p>}
    </div>
  );
}