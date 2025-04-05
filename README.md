# WhatsApp Campaign Manager

A powerful web application for managing WhatsApp marketing campaigns with AI-powered message generation.

## Features

- Create and manage WhatsApp marketing campaigns
- AI-powered message generation using OpenAI
- Contact list management
- Campaign analytics and tracking
- Integration with Twilio WhatsApp Business API
- User authentication and authorization
- Beautiful and responsive UI

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Twilio account with WhatsApp Business API access
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd whatsapp-campaign-manager
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit the `.env` file with your actual credentials:
- Add your Twilio credentials (Account SID, Auth Token, WhatsApp number)
- Add your OpenAI API key
- Set a secure SECRET_KEY for Flask

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Usage

1. Sign up for an account at `/signup`
2. Log in to access the dashboard
3. Create a new campaign
4. Add contacts to your campaign
5. Generate AI-powered messages or create custom messages
6. Schedule and send your campaign

## Development

- The application uses Flask as the web framework
- SQLAlchemy for database management
- Twilio for WhatsApp integration
- OpenAI for AI-powered message generation

## Directory Structure

```
whatsapp-campaign-manager/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── auth.py
│   ├── whatsapp.py
│   └── ai_service.py
├── templates/
├── static/
├── requirements/
├── .env.example
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 