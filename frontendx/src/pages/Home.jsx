import { Link } from "react-router-dom";
import { Search, Activity, AlertTriangle, Eye } from "lucide-react";

export default function Home() {

  const API = "http://127.0.0.1:5000";
  const features = [
    {
      icon: Search,
      title: "Automated Code Scanning",
      description:
        "Continuously scan your repositories for vulnerabilities, malicious code, and hidden security threats using advanced AI analysis.",
    },
    {
      icon: Activity,
      title: "ML-Based Anomaly Detection",
      description:
        "Detect unusual patterns across your builds and deployments with intelligent machine-learning-powered anomaly detection.",
    },
    {
      icon: Eye,
      title: "CI/CD Health Dashboard",
      description:
        "Monitor deployments, executions, build failures, and key operational metrics in real-time with a unified security dashboard.",
    },
    {
      icon: AlertTriangle,
      title: "Real-Time Alerts",
      description:
        "Receive instant notifications for security incidents, pipeline anomalies, and unexpected system behaviors.",
    },
  ];

  return (
    <div className="min-h-screen bg-[#061328] flex flex-col">

      {/* Built-in Navbar (instead of Header.jsx) */}
      <nav className="w-full bg-[#112240] border-b border-[#233554] py-4 px-6 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 bg-[#64ffda] rounded-md flex items-center justify-center text-[#061328] font-bold">
            VX
          </div>
          <span className="text-white text-xl font-semibold tracking-wide">
            VigilantX
          </span>
        </div>

        <div className="space-x-6 flex items-center">
          <Link
            to="/"
            className="text-[#ccd6f6] hover:text-white transition"
          >
            Home
          </Link>

          <Link
            to="/login"
            className="text-[#ccd6f6] hover:text-white transition"
          >
            Login
          </Link>

          <Link
            to="/signup"
            className="px-4 py-2 border border-[#64ffda] text-[#64ffda] rounded-lg hover:bg-[rgba(100,255,218,0.1)] hover:border-[#79ffe0] hover:text-[#79ffe0] transition"
          >
            Sign Up
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="text-center px-6 py-32 bg-gradient-to-br from-[#061328] to-[#112240] border-b border-[#233554]">
        <p className="text-[#ccd6f6] text-2xl mb-4 font-light tracking-wider">
          VigilantX
        </p>

        <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6 leading-tight tracking-tight">
          AI-Powered Security &<br />Pipeline Monitoring
        </h1>

        <p className="text-[#ccd6f6] text-xl md:text-2xl max-w-3xl mx-auto mb-12 leading-relaxed">
          Protect your CI/CD pipelines from malicious activity with intelligent
          monitoring, continuous analysis, and real-time threat detection.
        </p>

        <div className="flex justify-center items-center space-x-8">
          <Link
            to="/login"
            className="px-8 py-4 bg-[#64ffda] text-[#061328] rounded-lg font-bold text-lg"
          >
            Get Started
          </Link>


          <Link
            to="/signup"
            className="px-8 py-4 bg-transparent text-[#64ffda] rounded-lg font-bold text-lg border-2 border-[#64ffda] hover:bg-[rgba(100,255,218,0.1)] hover:border-[#79ffe0] hover:text-[#79ffe0] hover:-translate-y-0.5 transition-all"
          >
            Create an account
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-8 md:px-12 py-24 text-center">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-16 leading-snug">
          Unleash the Power of AI-Driven <br />
          Security & Pipeline Intelligence
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mt-10">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="p-8 border border-[#233554] rounded-xl bg-[#112240] shadow-lg hover:shadow-[0_12px_25px_rgba(0,0,0,0.3),0_0_15px_rgba(100,255,218,0.3)] hover:-translate-y-2 transition-all"
              >
                <div className="flex justify-center mb-6">
                  <Icon className="w-12 h-12 text-[#64ffda]" />
                </div>

                <h3 className="text-[#64ffda] text-2xl font-semibold mb-4">
                  {feature.title}
                </h3>

                <p className="text-[#ccd6f6] text-lg leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
