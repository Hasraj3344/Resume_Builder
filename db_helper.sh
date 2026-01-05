#!/bin/bash
# Database Helper Script for Resume Builder

DB="resume_builder.db"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Resume Builder Database Helper ===${NC}\n"

case "$1" in
    "users")
        echo -e "${GREEN}All Users:${NC}"
        sqlite3 $DB "SELECT id, email, full_name, created_at FROM users;" -header -column
        ;;
    "subscriptions")
        echo -e "${GREEN}Active Subscriptions:${NC}"
        sqlite3 $DB "
            SELECT u.email, s.plan_type, s.status, s.start_date, s.next_billing_date
            FROM users u
            JOIN subscriptions s ON u.id = s.user_id
            WHERE s.status = 'active';
        " -header -column
        ;;
    "usage")
        echo -e "${GREEN}Current Month Usage:${NC}"
        sqlite3 $DB "
            SELECT u.email, ur.month_year, ur.resumes_generated, ur.reset_date
            FROM users u
            JOIN usage_records ur ON u.id = ur.user_id
            WHERE ur.month_year = strftime('%Y-%m', 'now')
            ORDER BY u.email;
        " -header -column
        ;;
    "resumes")
        echo -e "${GREEN}Generated Resumes:${NC}"
        sqlite3 $DB "
            SELECT u.email, r.filename, r.created_at
            FROM users u
            JOIN resumes r ON u.id = r.user_id
            ORDER BY r.created_at DESC
            LIMIT 20;
        " -header -column
        ;;
    "sessions")
        echo -e "${GREEN}Active Sessions:${NC}"
        sqlite3 $DB "
            SELECT u.email, s.created_at, s.expires_at, s.revoked
            FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.expires_at > datetime('now')
            ORDER BY s.created_at DESC;
        " -header -column
        ;;
    "reset")
        if [ -z "$2" ]; then
            echo "Usage: ./db_helper.sh reset <email>"
            exit 1
        fi
        echo -e "${GREEN}Resetting usage for: $2${NC}"
        sqlite3 $DB "
            UPDATE usage_records
            SET resumes_generated = 0
            WHERE user_id = (SELECT id FROM users WHERE email = '$2')
              AND month_year = strftime('%Y-%m', 'now');
        "
        echo "Done! Usage reset to 0/3"
        ;;
    "query")
        echo -e "${GREEN}Custom Query Mode${NC}"
        echo "Enter your SQL query (or 'exit' to quit):"
        sqlite3 $DB -header -column
        ;;
    *)
        echo "Usage: ./db_helper.sh [command]"
        echo ""
        echo "Commands:"
        echo "  users          - List all users"
        echo "  subscriptions  - Show active subscriptions"
        echo "  usage          - Show current month usage"
        echo "  resumes        - List generated resumes"
        echo "  sessions       - Show active sessions"
        echo "  reset <email>  - Reset usage count for user"
        echo "  query          - Interactive SQL query mode"
        echo ""
        echo "Examples:"
        echo "  ./db_helper.sh users"
        echo "  ./db_helper.sh usage"
        echo "  ./db_helper.sh reset haswanthrajeshn@gmail.com"
        ;;
esac
