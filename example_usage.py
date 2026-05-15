"""
Example usage of RepoPilot - Demonstrates how to use the platform
"""

from pathlib import Path
from src.repopilot.analyzers import ASTAnalyzer, DependencyAnalyzer, CoverageAnalyzer
from src.repopilot.generators import DocGenerator, OnboardingGenerator


def main():
    """
    Example: Analyze the RepoPilot project itself
    """
    # Set the repository path (current project)
    repo_path = Path(".")
    
    print("=" * 60)
    print("RepoPilot - Repository Analysis Example")
    print("=" * 60)
    print()
    
    # 1. AST Analysis
    print("1. Performing AST Analysis...")
    print("-" * 60)
    ast_analyzer = ASTAnalyzer()
    ast_analyzer.analyze_directory(repo_path / "src")
    architecture = ast_analyzer.get_architecture_summary()
    
    print(f"✓ Total files analyzed: {architecture['total_files']}")
    print(f"✓ Total classes: {architecture['total_classes']}")
    print(f"✓ Total functions: {architecture['total_functions']}")
    print(f"✓ Total lines of code: {architecture['total_lines_of_code']:,}")
    print(f"✓ Average complexity: {architecture['average_complexity']}")
    print()
    
    # 2. Dependency Analysis
    print("2. Performing Dependency Analysis...")
    print("-" * 60)
    dep_analyzer = DependencyAnalyzer(repo_path)
    dependencies = dep_analyzer.analyze_project()
    
    print(f"✓ Total dependencies: {dependencies['total_dependencies']}")
    print(f"✓ External packages: {dependencies['external_packages']}")
    print(f"✓ Standard library modules: {dependencies['standard_library']}")
    print()
    
    if dependencies['external_packages_list']:
        print("External packages:")
        for pkg in dependencies['external_packages_list'][:5]:
            version = pkg.get('version', 'N/A')
            print(f"  - {pkg['name']} ({version})")
        if len(dependencies['external_packages_list']) > 5:
            print(f"  ... and {len(dependencies['external_packages_list']) - 5} more")
    print()
    
    # 3. Coverage Analysis
    print("3. Performing Coverage Analysis...")
    print("-" * 60)
    coverage_analyzer = CoverageAnalyzer(repo_path)
    coverage = coverage_analyzer.analyze_coverage()
    
    print(f"✓ Overall coverage: {coverage['overall_coverage']}%")
    print(f"✓ Total tests: {coverage['total_tests']}")
    print(f"✓ Total modules: {coverage['total_modules']}")
    print()
    
    test_breakdown = coverage.get('test_breakdown', {})
    print("Test breakdown:")
    print(f"  - Unit tests: {test_breakdown.get('unit', 0)}")
    print(f"  - Integration tests: {test_breakdown.get('integration', 0)}")
    print(f"  - Functional tests: {test_breakdown.get('functional', 0)}")
    print()
    
    if coverage.get('recommendations'):
        print("Recommendations:")
        for rec in coverage['recommendations'][:3]:
            print(f"  • {rec}")
    print()
    
    # 4. Generate Documentation
    print("4. Generating Documentation...")
    print("-" * 60)
    doc_gen = DocGenerator(repo_path)
    
    # Generate architecture documentation
    arch_doc = doc_gen.generate_architecture_docs(architecture)
    arch_path = doc_gen.save_documentation("GENERATED_ARCHITECTURE.md", arch_doc)
    print(f"✓ Architecture documentation saved to: {arch_path}")
    
    # Generate dependency documentation
    dep_doc = doc_gen.generate_dependency_docs(dependencies)
    dep_path = doc_gen.save_documentation("GENERATED_DEPENDENCIES.md", dep_doc)
    print(f"✓ Dependency documentation saved to: {dep_path}")
    print()
    
    # 5. Generate Onboarding Report
    print("5. Generating Onboarding Report...")
    print("-" * 60)
    onboarding_gen = OnboardingGenerator(repo_path)
    report = onboarding_gen.generate_onboarding_report(
        architecture,
        dependencies,
        coverage,
        ast_analyzer.analyses
    )
    report_path = onboarding_gen.save_onboarding_report(report)
    print(f"✓ Onboarding report saved to: {report_path}")
    print()
    
    # Summary
    print("=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print()
    print("Generated files:")
    print(f"  - {arch_path}")
    print(f"  - {dep_path}")
    print(f"  - {report_path}")
    print()
    print("Next steps:")
    print("  1. Review the generated documentation in the docs/ directory")
    print("  2. Check the recommendations in the coverage report")
    print("  3. Start the API server: python -m uvicorn src.repopilot.api.main:app --reload")
    print("  4. Visit http://localhost:8000/docs for interactive API documentation")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nMake sure you have:")
        print("  1. Installed all dependencies: pip install -r requirements.txt")
        print("  2. Run from the project root directory")

# Made with Bob
