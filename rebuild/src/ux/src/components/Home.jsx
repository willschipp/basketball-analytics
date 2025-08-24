import { version } from '../../package.json';

{/* <div className="d-flex vh-100 justify-content-center align-items-center"></div> */}

function Home() {
    return (
        <div className="d-flex justify-content-center align-items-center vh-100 w-75">
            <div className="card text-center w-75">
                <div className="card-body">
                    <h5 className="card-title">Welcome to AthlosCore!</h5>
                    <h6 className="card-subtitle mb-2 text-muted">August, 2025 Version v{version}</h6>
                    <p className="card-text">
                        [Need some content here]
                    </p>
                </div>
            </div>            
        </div>
    );
}

export default Home