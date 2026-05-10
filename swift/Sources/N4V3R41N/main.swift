import ArgumentParser
import Foundation

@main
struct N4V3R41N: ParsableCommand {
    static let configuration = CommandConfiguration(
        abstract: "The Ultimate iOS Exploitation Suite (Swift)",
        subcommands: [
            ListDevices.self,
            Checkm8.self
        ]
    )

    struct ListDevices: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "List connected iOS devices")
        func run() throws {
            print("[v7-SWIFT] Listing devices...")
        }
    }

    struct Checkm8: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Run Checkm8 exploit")
        func run() throws {
            print("[v7-SWIFT] Running Checkm8...")
        }
    }
}
