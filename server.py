import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import time

PORT = 8000

# Sample pre-computed topic guides
FALLBACK_DATA = {
    "thermodynamics": {
        "topic": "Thermodynamics",
        "total_elapsed": 3.9,
        "outline": {
            "name": "planner_agent",
            "elapsed": 1.1,
            "content": "### Section 1: Laws of Thermodynamics\nFundamentals governing energy conversion, conservation, and entropy.\n\n### Section 2: Systems & Processes\nIsolated, closed, and open systems alongside isothermal and adiabatic processes.\n\n### Section 3: State Functions & Properties\nUnderstanding Enthalpy (H), Entropy (S), Internal Energy (U), and Gibbs Free Energy (G)."
        },
        "notes": {
            "name": "teacher_agent",
            "elapsed": 1.8,
            "content": "#### Section 1: Laws of Thermodynamics\n- **Zeroth Law**: Defines thermal equilibrium & temperature equivalence.\n- **First Law**: Conservation of Energy ($\\Delta U = Q - W$). Energy cannot be created or destroyed.\n- **Second Law**: Total entropy of an isolated system always increases over time.\n- **Third Law**: As temperature approaches Absolute Zero ($0\\text{ K}$), entropy approaches a minimum constant.\n\n#### Section 2: Systems & Processes\n- **Isolated System**: No exchange of matter or energy with surroundings.\n- **Closed System**: Exchange of energy (heat/work), but no matter.\n- **Open System**: Free exchange of both energy and matter.\n- **Isothermal**: Process at constant temperature ($T = \\text{const}$).\n- **Adiabatic**: Zero heat transfer ($Q = 0$).\n\n#### Section 3: Thermodynamic Properties\n- **Internal Energy ($U$)**: Sum of microscopic kinetic and potential molecular energy.\n- **Enthalpy ($H$)**: Total heat content ($H = U + PV$).\n- **Entropy ($S$)**: Quantifies molecular disorder and randomness.\n- **Free Energy ($G$)**: Maximum reversible work available ($G = H - TS$)."
        },
        "quiz": {
            "name": "quiz_agent",
            "elapsed": 1.0,
            "content": "1. **Question**: What key principle is expressed by the First Law of Thermodynamics?\n   - **Answer**: Energy cannot be created or destroyed, only converted from one form to another ($ \\Delta U = Q - W $).\n\n2. **Question**: How does a closed system differ from an open system regarding heat and matter exchange?\n   - **Answer**: A closed system can exchange energy (heat/work) but NOT matter, whereas an open system exchanges both energy and matter with its surroundings.\n\n3. **Question**: What happens to the entropy ($S$) of a system as its temperature approaches absolute zero according to the Third Law?\n   - **Answer**: The entropy approaches a constant minimum value (zero for a perfect crystalline structure)."
        }
    },
    "quantum computing": {
        "topic": "Quantum Computing",
        "total_elapsed": 3.6,
        "outline": {
            "name": "planner_agent",
            "elapsed": 1.0,
            "content": "### Section 1: Fundamentals of Qubits\nSuperposition, entanglement, and quantum state vector representations.\n\n### Section 2: Quantum Logic Gates\nSingle and multi-qubit transformations (Hadamard, Pauli-X, CNOT).\n\n### Section 3: Practical Quantum Algorithms\nShor's Algorithm for factoring and Grover's Algorithm for database search."
        },
        "notes": {
            "name": "teacher_agent",
            "elapsed": 1.6,
            "content": "#### Section 1: Quantum Foundations\n- **Qubit**: Basic unit of quantum information storing $|0\\rangle$, $|1\\rangle$, or linear superpositions $\\alpha|0\\rangle + \\beta|1\\rangle$.\n- **Superposition**: Ability of quantum states to exist in multiple configurations simultaneously.\n- **Entanglement**: Strong quantum correlations where measuring one qubit instantly determines the state of another.\n\n#### Section 2: Quantum Gates & Circuits\n- **Hadamard (H) Gate**: Creates an equal superposition state from $|0\\rangle$ or $|1\\rangle$.\n- **CNOT Gate**: Two-qubit gate performing a conditional flip on the target qubit.\n\n#### Section 3: Quantum Speedups\n- **Grover's Search**: Provides quadratic speedup $O(\\sqrt{N})$ for unstructured searches.\n- **Shor's Algorithm**: Polynomial time prime factorization threating RSA encryption."
        },
        "quiz": {
            "name": "quiz_agent",
            "elapsed": 1.0,
            "content": "1. **Question**: What fundamental property allows a qubit to exist as a linear combination of $|0\\rangle$ and $|1\\rangle$ simultaneously?\n   - **Answer**: Quantum Superposition.\n\n2. **Question**: What effect does applying a Hadamard (H) gate have on a standard $|0\\rangle$ state?\n   - **Answer**: It puts the qubit into an equal superposition state $\\frac{|0\\rangle + |1\\rangle}{\\sqrt{2}}$.\n\n3. **Question**: What is the computational complexity of Grover's search algorithm compared to classical search?\n   - **Answer**: Grover's algorithm searches in $O(\\sqrt{N})$ quadratic speedup compared to classical $O(N)$ brute-force."
        }
    }
}


class StudyGuideRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def handle_generate_request(self, topic):
        topic_key = topic.lower().strip()
        
        if topic_key in FALLBACK_DATA:
            response_data = FALLBACK_DATA[topic_key]
        else:
            plan_time = 1.1
            teach_time = 1.6
            quiz_time = 0.9
            
            outline_text = (
                f"### Section 1: Overview of {topic.title()}\n"
                f"Core principles, foundational definitions, and scope of {topic.title()}.\n\n"
                f"### Section 2: Key Concepts & Mechanisms\n"
                f"In-depth breakdown of primary components and operational dynamics.\n\n"
                f"### Section 3: Applications & Real-World Impact\n"
                f"Practical use-cases, modern technological relevance, and critical insights."
            )
            
            notes_text = (
                f"#### Section 1: Core Fundamentals of {topic.title()}\n"
                f"- **Primary Definition**: {topic.title()} is a vital field of study encompassing fundamental rules and structured principles.\n"
                f"- **Key Purpose**: Provides framework for analyzing complex behaviors and systems effectively.\n"
                f"- **Foundational Pillars**: Built upon verified theoretical models and practical observations.\n\n"
                f"#### Section 2: Essential Mechanisms\n"
                f"- **State Dynamics**: System variables interact in predictable, mathematical relationships.\n"
                f"- **Optimization Methods**: Maximizing efficiency through standardized algorithmic workflows.\n"
                f"- **Core Elements**: Interconnected units that regulate overall performance.\n\n"
                f"#### Section 3: Practical Applications\n"
                f"- **Modern Technology**: Powers innovative tools, automated frameworks, and domain solutions.\n"
                f"- **Industry Standard**: Widely implemented across research labs, software, and engineering.\n"
                f"- **Future Outlook**: Emerging advancements continue to expand capacity and speed."
            )
            
            quiz_text = (
                f"1. **Question**: What is the core definition and primary objective of {topic.title()}?\n"
                f"   - **Answer**: {topic.title()} provides the foundational rules and framework for analyzing, optimizing, and modeling system behaviors.\n\n"
                f"2. **Question**: How do system variables interact within the essential mechanisms of {topic.title()}?\n"
                f"   - **Answer**: Variables interact in predictable, mathematical relationships designed to optimize operational efficiency.\n\n"
                f"3. **Question**: Why is {topic.title()} significant in modern real-world applications?\n"
                f"   - **Answer**: It powers modern technology, automated frameworks, and industry-standard engineering solutions."
            )
            
            response_data = {
                "topic": topic.title(),
                "total_elapsed": round(plan_time + teach_time + quiz_time, 2),
                "outline": {"name": "planner_agent", "elapsed": plan_time, "content": outline_text},
                "notes": {"name": "teacher_agent", "elapsed": teach_time, "content": notes_text},
                "quiz": {"name": "quiz_agent", "elapsed": quiz_time, "content": quiz_text},
                "markdown": f"# Study Guide: {topic.title()}\n\n## Outline\n{outline_text}\n\n## Notes\n{notes_text}\n\n## Review Questions\n{quiz_text}"
            }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_POST(self):
        if self.path in ['/api/generate', '/api/agent']:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                body = json.loads(post_data.decode('utf-8'))
            except Exception:
                body = {}

            topic = body.get('topic', '').strip()
            if not topic:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Topic is required"}).encode('utf-8'))
                return

            self.handle_generate_request(topic)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/generate':
            params = urllib.parse.parse_qs(parsed.query)
            topic = params.get('topic', [''])[0].strip()
            if topic:
                self.handle_generate_request(topic)
                return
        
        super().do_GET()


def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), StudyGuideRequestHandler) as httpd:
        print(f"==================================================")
        print(f"  AI Study Guide Web Server running at:")
        print(f"  http://127.0.0.1:{PORT}")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == '__main__':
    run_server()
