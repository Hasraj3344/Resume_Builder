#!/bin/bash

# Resume Builder Docker Deployment Script
# Usage: ./deploy.sh [start|stop|restart|logs|update|backup]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    print_success "Docker and Docker Compose are installed"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.production .env
        print_warning "Please edit .env file with your configuration"
        print_warning "Run: nano .env"
        exit 1
    fi
    print_success ".env file found"
}

# Create necessary directories
create_dirs() {
    mkdir -p data output uploads
    print_success "Created necessary directories"
}

# Start services
start() {
    print_success "Starting Resume Builder..."
    docker-compose up -d --build

    echo ""
    print_success "Services started successfully!"
    echo ""
    echo "Access your application at:"
    echo "  Frontend: http://localhost"
    echo "  Backend:  http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "View logs with: ./deploy.sh logs"
}

# Stop services
stop() {
    print_success "Stopping Resume Builder..."
    docker-compose down
    print_success "Services stopped"
}

# Restart services
restart() {
    print_success "Restarting Resume Builder..."
    docker-compose restart
    print_success "Services restarted"
}

# View logs
logs() {
    docker-compose logs -f
}

# Update application
update() {
    print_success "Updating Resume Builder..."

    # Pull latest code
    if [ -d .git ]; then
        git pull origin main
        print_success "Code updated"
    fi

    # Rebuild and restart
    docker-compose down
    docker-compose up -d --build

    print_success "Application updated successfully!"
}

# Backup database
backup() {
    BACKUP_DIR="./backups"
    mkdir -p "$BACKUP_DIR"

    BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).db"

    print_success "Creating database backup..."
    docker-compose exec -T backend sqlite3 /data/resume_builder.db ".backup /data/backup.db"
    docker cp resume-builder-backend:/data/backup.db "$BACKUP_FILE"

    print_success "Backup created: $BACKUP_FILE"
}

# Show status
status() {
    print_success "Container Status:"
    docker-compose ps

    echo ""
    print_success "Health Checks:"

    # Check backend health
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend: Healthy"
    else
        print_error "Backend: Unhealthy or not running"
    fi

    # Check frontend health
    if curl -sf http://localhost/health > /dev/null 2>&1; then
        print_success "Frontend: Healthy"
    else
        print_error "Frontend: Unhealthy or not running"
    fi
}

# Show usage
usage() {
    echo "Resume Builder Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the application"
    echo "  stop     - Stop the application"
    echo "  restart  - Restart the application"
    echo "  logs     - View application logs"
    echo "  update   - Update and rebuild the application"
    echo "  backup   - Backup the database"
    echo "  status   - Show service status"
    echo "  help     - Show this help message"
    echo ""
}

# Main script
main() {
    check_docker

    case "${1:-help}" in
        start)
            check_env
            create_dirs
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs
            ;;
        update)
            update
            ;;
        backup)
            backup
            ;;
        status)
            status
            ;;
        help|*)
            usage
            ;;
    esac
}

main "$@"
