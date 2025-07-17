#!/bin/bash

echo "🎨 OpenAlgo CSS Build Test"
echo "=========================="

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

echo "✅ npm version: $(npm --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ npm install failed"
    exit 1
fi

echo "✅ Dependencies installed"

# Create static directory if it doesn't exist
mkdir -p static/css

# Build CSS
echo ""
echo "🎨 Building Tailwind CSS..."
npm run build:css

if [ $? -ne 0 ]; then
    echo "❌ CSS build failed"
    exit 1
fi

echo "✅ CSS build completed"

# Check if CSS file was created
if [ -f "static/css/main.css" ]; then
    echo "✅ CSS file created: static/css/main.css"
    echo "📄 File size: $(wc -c < static/css/main.css) bytes"
    
    # Check if CSS contains DaisyUI classes
    if grep -q "daisyui" static/css/main.css; then
        echo "✅ DaisyUI styles found in CSS"
    else
        echo "⚠️  DaisyUI styles not found in CSS"
    fi
    
    # Check if CSS contains Tailwind utilities
    if grep -q "tw-" static/css/main.css; then
        echo "✅ Tailwind utilities found in CSS"
    else
        echo "⚠️  Tailwind utilities not found in CSS"
    fi
else
    echo "❌ CSS file was not created"
    exit 1
fi

echo ""
echo "🎉 CSS build test completed successfully!"
echo "The application should now display properly with DaisyUI styling." 