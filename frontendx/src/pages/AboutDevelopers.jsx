import DashboardCard from "../components/DashboardCard";
import { Users } from "lucide-react";

// ✅ Import local images from /src/asset/
import ShreyashImg from "../asset/Shreyash.jpg";
import OmImg from "../asset/om.jpg";
import AmanImg from "../asset/aman.jpg";
import KishuImg from "../asset/kishu.jpg";
import GroupImg from "../asset/Group.jpg"; // ✅ Group photo
const API = "http://127.0.0.1:5000";

export default function AboutDevelopers() {
  const team = {
    leader: {
      name: "Shreyash Ghare",
      title: "Cybersecurity Aficionado • DevSecOps • Backend Developer",
      img: ShreyashImg,
    },
    members: [
      {
        name: "Omprasad Tilak",
        title: "Co-Lead • Frontend • AI-ML • Backend Developer",
        img: OmImg,
      },
      {
        name: "Aman Gupta",
        title: "Documentation • Frontend Developer • UI/UX",
        img: AmanImg,
      },
      {
        name: "Kishu Anand Raj",
        title: "Management • UI/UX • Tester",
        img: KishuImg,
      },
    ],
  };

  return (
    <div className="p-6 md:p-10">
      {/* Header */}
      <h1 className="text-4xl font-bold text-white mb-6 flex items-center">
        <Users className="w-8 h-8 mr-3 text-[#64ffda]" />
        About Developers
      </h1>

      {/* Project Title */}
      <DashboardCard title="Innovative Project">
        <div className="text-[#ccd6f6] text-center">
          <h2 className="text-2xl font-semibold text-[#64ffda] mb-2">
            CI/CD Pipeline Integrity Monitoring & Code Injection Detection System
          </h2>
          <p className="text-[#8892b0] text-sm mb-8">
            A collaborative project focusing on automated code scanning, CI/CD integrity, and real-time security monitoring.
          </p>

          {/* Leader Section */}
          <div className="flex flex-col items-center mb-10">
            <div className="relative">
              <img
                src={team.leader.img}
                alt={team.leader.name}
                className="w-32 h-32 rounded-full border-4 border-[#64ffda] shadow-lg object-cover"
              />
            </div>
            <h3 className="mt-4 text-xl font-bold text-[#ccd6f6]">{team.leader.name}</h3>
            <p className="text-[#8892b0] text-sm">{team.leader.title}</p>
            <p className="mt-2 text-[#64ffda] font-semibold text-sm">Team Leader</p>
          </div>

          {/* Members Section */}
          <div className="grid md:grid-cols-3 sm:grid-cols-1 gap-8 justify-center mb-16">
            {team.members.map((m, i) => (
              <div
                key={i}
                className="flex flex-col items-center bg-[#0a192f] p-6 rounded-2xl border border-[#233554] hover:border-[#64ffda] transition-all"
              >
                <div className="relative">
                  <img
                    src={m.img}
                    alt={m.name}
                    className="w-24 h-24 rounded-full border-2 border-[#64ffda] object-cover"
                  />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-[#ccd6f6]">{m.name}</h3>
                <p className="text-[#8892b0] text-sm text-center">{m.title}</p>
              </div>
            ))}
          </div>

          {/* 🧩 TEAM VMX Section (Photo Left, Text Right) */}
          <div className="grid md:grid-cols-2 sm:grid-cols-1 items-center gap-10 text-left">
            {/* Left: Group Photo */}
            <div className="flex justify-center">
              <div className="rounded-2xl overflow-hidden shadow-lg border border-[#233554] w-[80%] md:w-[90%]">
                <img
                  src={GroupImg}
                  alt="Team VMX Group Photo"
                  className="w-full h-auto object-cover"
                />
              </div>
            </div>

            {/* Right: Description */}
            <div className="space-y-4">
              <h2 className="text-3xl font-bold text-[#64ffda]">TEAM VIGILANT MAVERICKS</h2>
              <p className="text-[#ccd6f6] leading-relaxed">
                Team VMX represents the fusion of development, security, and operations into one powerful force.
                Our mission is to create secure, automated CI/CD ecosystems that ensure code integrity,
                detect vulnerabilities, and prevent insider threats — from commit to deployment.
              </p>
              <p className="text-[#8892b0] italic">
                “In DevSecOps, security is not a gate — it’s the guardian woven into every line of code.”
              </p>
              <p className="text-[#64ffda] font-semibold">
                🚀 United under innovation • Driven by trust • Built with security
              </p>
            </div>
          </div>
        </div>
      </DashboardCard>
    </div>
  );
}

