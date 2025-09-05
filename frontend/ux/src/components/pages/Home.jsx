import { useNavigate } from 'react-router-dom';

function Home() {

    const navigate = useNavigate();

    const handleUpload = (e) => {
        e.preventDefault()
        navigate('/videos');
    }


    return (
        <div className="container-fluid d-flex justify-content-center align-items-center h-100 w-100 bg-white text-primary-dark" style={{ color: "#162948" }}>
            <div className="row w-100 h-100 mt-4">
                {/* <!-- col 1 --> */}
                <div className="col-md-6 d-flex flex-column gap-3">
                    {/* <!-- row 1 --> */}
                    <div className="card p-3 text-center">
                        <button className="btn btn-lg btn-outline-secondary w-100" onClick={handleUpload} style={{ backgroundColor: "#f15e22", color: "white", borderColor: "#f15e22" }}>
                            Upload New Video
                        </button>
                    </div>

                    {/* <!-- row 2 --> */}
                    <div className="card p-3">
                        <h4>Upload Status</h4>
                        <p>[game name]</p>
                    </div>

                    {/* <!-- row 3 --> */}
                    <div className="card p-3">
                        <h4>Quick Links</h4>
                        <div className="d-flex gap-2">
                        <button className="btn btn-outline-primary">Highlights</button>
                        <button className="btn btn-outline-primary">Player Insight</button>
                        </div>
                    </div>
                </div>

                {/* <!-- col 2 --> */}
                <div className="col-md-6 d-flex flex-column">
                    {/* <!-- row 1 --> */}
                    <div className="card p-3">
                        <h4>Recent Games</h4>
                        <table className="table">
                        <tbody>
                            <tr>
                            <td>[game name]</td>
                            <td>[score]</td>
                            </tr>
                            <tr>
                            <td>[game name]</td>
                            <td>[score]</td>
                            </tr>
                            <tr>
                            <td>[game name]</td>
                            <td>[score]</td>
                            </tr>
                        </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

    );
}

export default Home