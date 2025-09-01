import { useState } from 'react';

function UploadForm({ refreshFunction }) {

    const [file,setFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');

    const handleFileChange = (e) => {
        if (e.target.files.length > 0) {
            //have a file
            setFile(e.target.files[0]);//get the first one
            setUploadStatus('');
        }
    }
    
    const handleUpload = async (e) => {
        e.preventDefault();

        if (!file || file === null) {
            setUploadStatus('Please select a file');
            return; //done here
        } //end if

        console.log(file);

        setUploadStatus('Uploading...');

        const formData = new FormData();
        formData.append('file',file);

        try {
            const response = await fetch('/api/v1/videos', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                setUploadStatus('Upload finished.  Processing started');
                if (refreshFunction) {
                    refreshFunction(); //refresh
                }
            } else {
                setUploadStatus('Upload failed.  Please try again.');                
            } //end if
        } catch (error) {
            setUploadStatus('Error in processing');
            console.error('error uploading',error);
        }
    }

    return (
    <>
        <div className="card p-3">
            <h4>Upload Game</h4>
            <div className="input-group mb-3">
                <input type="file" class="form-control" aria-label="Upload game video" onChange={handleFileChange}/>
                <button className="btn btn-outline-secondary" type="button" id="upload-button" onClick={handleUpload} style={{ backgroundColor: "#f15e22", color: "white", borderColor: "#f15e22" }}>Upload</button>                
            </div>
            {(uploadStatus) ? (<p>{uploadStatus}</p>) : (<></>)}
        </div>    
    </>
    );
}

export default UploadForm