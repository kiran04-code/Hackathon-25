import cv2
import sqlite3
import geocoder
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Database setup
conn = sqlite3.connect("attendance.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY, name TEXT, location TEXT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
conn.commit()

def scan_qr():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        _, img = cap.read()
        data, bbox, _ = detector.detectAndDecode(img)
        if data:
            cap.release()
            cv2.destroyAllWindows()
            return data  # QR Code data

        cv2.imshow("QR Scanner", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

def get_location():
    g = geocoder.ip("me")
    return g.latlng if g.ok else "Location not found"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    qr_data = scan_qr()
    if qr_data:
        location = get_location()
        c.execute("INSERT INTO attendance (name, location) VALUES (?, ?)", (qr_data, str(location)))
        conn.commit()
        return jsonify({"success": True, "name": qr_data, "location": location})
    return jsonify({"success": False})

@app.route("/attendance")
def attendance():
    c.execute("SELECT * FROM attendance")
    data = c.fetchall()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
