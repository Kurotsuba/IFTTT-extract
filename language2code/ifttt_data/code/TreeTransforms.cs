using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ifttt
{
    public class TreeTransforms
    {
        public static AstNode MoveTextParamsFromActionToTrigger(AstNode an)
        {
            an = an.DeepCopy();

            // get the action parameters
            var p = an["ACTION"]["FUNC"]["PARAMS"];
            if (p.Children.Count == 0) return an;

            // find parameters that contain a "{{" in their value
            var complex = p.Children.Where(c => c.Children.Count > 0 && c[0].Name.Contains("{{")).ToArray();
            int paramCount = complex.Length;

            // no params? nothing to do.
            if (paramCount == 0) return an;

            // too many params? can't handle.
            if (paramCount > 2) return an;

            var op = new AstNode("OUTPARAMS");
            an["TRIGGER"]["FUNC"].Children.Add(op);

            if (paramCount == 2)
            {
                var x1 = complex[0];
                var x2 = complex[1];

                if (x1[0].Name.Length < x2[0].Name.Length) { var t = x1; x1 = x2; x2 = t; }

                MoveWithTrace(x1, 0, op, "MESSAGE:Text");
                MoveWithTrace(x2, 0, op, "SUBJECT:Text");
            }
            else if (paramCount == 1)
            {
                MoveWithTrace(complex[0], 0, op, "MESSAGE:Text");
            }

            return an;
        }

        public static AstNode Rewrite(AstNode tree, AstNode from, AstNode to, List<AstNode> matchVars, List<AstNode> resultVars)
        {
            if (Match(tree, from, matchVars))
            {
                return Instantiate(to, matchVars, resultVars);
            }
            throw new Exception("failed to match!");
        }

        public static bool Match(AstNode tree, AstNode pattern, List<AstNode> vars)
        {
            if (pattern.Variable)
            {
                if (pattern.Name != "*" && string.Compare(tree.Name, pattern.Name) != 0) return false;
                int id = pattern.VariableID - 1;
                while (vars.Count <= id) vars.Add(null);
                vars[id] = tree;
                return true;
            }

            if (tree.Children.Count != pattern.Children.Count) return false;

            for (int i = 0; i < tree.Children.Count; ++i)
                if (!Match(tree.Children[i], pattern.Children[i], vars))
                    return false;

            return true;
        }


        private static AstNode Instantiate(AstNode tree, List<AstNode> vars, List<AstNode> rVars)
        {
            if (tree.Variable)
            {
                int id = tree.VariableID - 1;
                while (rVars.Count <= id) rVars.Add(null);
                return rVars[id] = (vars[id].DeepCopy());
            }

            var n = new AstNode { Name = tree.Name };
            foreach (var c in tree.Children)
                n.Children.Add(Instantiate(c, vars, rVars));
            return n;
        }

        private static void MoveWithTrace(AstNode oldParent, int index, AstNode newParent, string traceName)
        {
            var msg = new AstNode(traceName, oldParent[index].DeepCopy());
            newParent.Children.Add(msg);
            oldParent.Children[index] = new AstNode("__" + traceName + "__");
        }
    }
}
