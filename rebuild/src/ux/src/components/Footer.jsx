
import './styles/Footer.css';
import { version } from '../../package.json';

function Footer() {
    return (
        <div id="footer" className="sticky-bottom">
            &copy; AthlosCore 2025 - Version v{version}
        </div>
    );
}

export default Footer