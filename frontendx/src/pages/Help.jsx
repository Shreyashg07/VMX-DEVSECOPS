import { HelpCircle, Mail, BookOpen } from "lucide-react";
const API = "http://127.0.0.1:5000";

export default function HelpPage() {
  return (
    <div className="p-6 md:p-10">
      <h1 className="text-4xl font-bold text-white mb-6 flex items-center">
        <HelpCircle className="w-8 h-8 mr-3 text-[#64ffda]" />
        Help & Support
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

        <div className="bg-[#112240] p-6 rounded-xl border border-[#233554] shadow-lg">
          <h2 className="text-2xl font-semibold text-[#64ffda] mb-3">Documentation</h2>
          <p className="text-[#ccd6f6] mb-3">
            Explore our official docs for full API, pipeline, and security model reference.
          </p>
          <a className="text-[#64ffda]" href="#">
            <BookOpen className="inline-block mr-2" /> Read Docs
          </a>
        </div>

        <div className="bg-[#112240] p-6 rounded-xl border border-[#233554] shadow-lg">
          <h2 className="text-2xl font-semibold text-[#64ffda] mb-3">Support</h2>
          <p className="text-[#ccd6f6] mb-3">
            Need help or encountering an issue? Reach out to our support team.
          </p>
          <a className="text-[#64ffda]" href="#">
            <Mail className="inline-block mr-2" /> Contact Support
          </a>
        </div>

      </div>
    </div>
  );
}
